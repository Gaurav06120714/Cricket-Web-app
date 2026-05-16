import re
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ============================================================
# PAGE CONFIG  (must be first Streamlit call)
# ============================================================

st.set_page_config(
    page_title="🏏 Cricket Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# GLOBAL CSS THEME
# ============================================================

st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0a1628; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #0d2137; border-right: 1px solid #1e3a5f; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e3a5f, #0d2137);
        border: 1px solid #2d5a8e;
        border-radius: 12px;
        padding: 16px;
    }

    /* Headers */
    h1, h2, h3 { color: #e8c547 !important; }

    /* Text */
    p, label, .stMarkdown { color: #c8d8e8 !important; }

    /* Selectbox and inputs */
    .stSelectbox > div > div { background-color: #1e3a5f; color: white; }

    /* Tabs */
    .stTabs [data-baseweb="tab"] { background-color: #1e3a5f; color: #c8d8e8; border-radius: 8px 8px 0 0; }
    .stTabs [aria-selected="true"] { background-color: #e8c547 !important; color: #0a1628 !important; }

    /* Dataframe */
    .stDataFrame { border: 1px solid #2d5a8e; border-radius: 8px; }

    /* Buttons */
    .stButton > button { background: linear-gradient(135deg, #e8c547, #d4a017); color: #0a1628; font-weight: bold; border: none; border-radius: 8px; }

    /* Radio buttons */
    .stRadio > div { color: #c8d8e8; }

    /* Success/error messages */
    .stSuccess { background-color: #1a4a2e; border: 1px solid #2d8a4e; }
    .stError { background-color: #4a1a1a; border: 1px solid #8a2d2d; }

    /* Custom card */
    .cricket-card {
        background: linear-gradient(135deg, #1e3a5f, #0d2137);
        border: 1px solid #2d5a8e;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
        text-align: center;
    }

    /* Medal styles */
    .medal-gold { color: #FFD700; font-size: 1.2em; }
    .medal-silver { color: #C0C0C0; font-size: 1.2em; }
    .medal-bronze { color: #CD7F32; font-size: 1.2em; }

    /* Hero section */
    .hero-title {
        font-size: 3em;
        font-weight: 900;
        color: #e8c547;
        text-align: center;
        text-shadow: 0 0 30px rgba(232,197,71,0.4);
        margin-bottom: 0.2em;
    }
    .hero-subtitle {
        font-size: 1.2em;
        color: #c8d8e8;
        text-align: center;
        margin-bottom: 1.5em;
    }
    .stat-card {
        background: linear-gradient(135deg, #1e3a5f, #0d2137);
        border: 1px solid #2d5a8e;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin: 6px;
    }
    .stat-card .stat-number {
        font-size: 2.2em;
        font-weight: 800;
        color: #e8c547;
    }
    .stat-card .stat-label {
        font-size: 0.9em;
        color: #8ab4c8;
        margin-top: 4px;
    }
    .feature-card {
        background: linear-gradient(135deg, #162840, #0d2137);
        border: 1px solid #2d5a8e;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        height: 140px;
    }
    .feature-card .fc-icon { font-size: 2em; }
    .feature-card .fc-title { color: #e8c547; font-weight: 700; margin-top: 8px; font-size: 1em; }
    .feature-card .fc-desc { color: #8ab4c8; font-size: 0.82em; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CHART THEME
# ============================================================

CHART_THEME = {
    "paper_bgcolor": "#0a1628",
    "plot_bgcolor": "#0d2137",
    "font": {"color": "#c8d8e8", "family": "Arial"},
    "xaxis": {"gridcolor": "#1e3a5f", "linecolor": "#2d5a8e"},
    "yaxis": {"gridcolor": "#1e3a5f", "linecolor": "#2d5a8e"},
    "colorway": ["#e8c547", "#4da6ff", "#ff6b6b", "#51cf66", "#f59f00", "#cc5de8"],
}


def apply_theme(fig):
    fig.update_layout(**CHART_THEME, height=420, margin=dict(l=20, r=20, t=40, b=20))
    return fig


# ============================================================
# HELPERS
# ============================================================

NUMERIC_COLS = [
    "Mat", "Inns", "Runs", "Ave", "SR", "100", "50", "HS", "BF", "NO", "0",
    "Wkts", "Econ", "4", "5", "10", "Balls", "Overs", "Ct", "St", "Dis",
    "Mdns", "Ct Wk", "Ct Fi",
]


def extract_country(player_name: str) -> str:
    """Extract country from 'Player Name (Country)' format."""
    match = re.search(r'\(([^)]+)\)', str(player_name))
    return match.group(1) if match else "Unknown"


def clean_player_name(player_name: str) -> str:
    """Remove country code from player name."""
    return re.sub(r'\s*\([^)]*\)', '', str(player_name)).strip()


def medal(rank: int) -> str:
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    return str(rank)


@st.cache_data
def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip()
    obj_cols = df.select_dtypes(include=["object"]).columns
    for col in obj_cols:
        df[col] = df[col].astype(str).str.strip()
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna("Unknown")
    # Drop unnamed index columns
    drop_cols = [c for c in df.columns if c.startswith("Unnamed")]
    df = df.drop(columns=drop_cols, errors="ignore")
    return df


@st.cache_data
def load_all_data() -> dict:
    base = Path("cleaned_data")
    keys = [
        "odi_batting", "odi_bowling", "odi_fielding",
        "t20_batting", "t20_bowling", "t20_fielding",
        "test_batting", "test_bowling", "test_fielding",
    ]
    result = {}
    for key in keys:
        path = base / f"{key}.csv"
        if path.exists():
            try:
                result[key] = _clean_df(pd.read_csv(path))
            except Exception:
                result[key] = None
        else:
            result[key] = None
    return result


DATA = load_all_data()


def get_batting_df(fmt: str):
    return DATA.get(f"{fmt.lower()}_batting")


def get_bowling_df(fmt: str):
    return DATA.get(f"{fmt.lower()}_bowling")


def get_fielding_df(fmt: str):
    return DATA.get(f"{fmt.lower()}_fielding")


def safe_val(series, default=0):
    try:
        v = float(series)
        return v if not np.isnan(v) else default
    except Exception:
        return default


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.markdown("""
<div style='text-align:center; padding: 12px 0;'>
  <span style='font-size:2.4em;'>🏏</span><br>
  <span style='color:#e8c547; font-weight:800; font-size:1.1em;'>Cricket Analytics</span><br>
  <span style='color:#8ab4c8; font-size:0.75em;'>Professional Stats Dashboard</span>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Home",
        "📊 Dashboard",
        "👤 Player Analysis",
        "⚖️ Compare Players",
        "🏆 Leaderboards",
        "🌍 Country Analytics",
        "🔍 Search",
        "📥 Downloads",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='color:#8ab4c8; font-size:0.8em; padding: 8px 0;'>
<b style='color:#e8c547;'>📋 Formats Available</b><br>
• ODI — One Day International<br>
• T20 — Twenty20 International<br>
• Test — Test Cricket<br><br>
<b style='color:#e8c547;'>⚙️ Last Updated</b><br>
January 2026
</div>
""", unsafe_allow_html=True)

# ============================================================
# PAGE: HOME
# ============================================================

if page == "🏠 Home":
    st.markdown('<div class="hero-title">🏏 Cricket Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Explore comprehensive statistics across ODI, T20, and Test cricket</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Aggregate totals across all formats
    all_batting = [DATA.get(k) for k in ["odi_batting", "t20_batting", "test_batting"] if DATA.get(k) is not None]
    all_bowling = [DATA.get(k) for k in ["odi_bowling", "t20_bowling", "test_bowling"] if DATA.get(k) is not None]

    total_players = sum(len(df["Player"].unique()) for df in all_batting)
    total_runs = int(sum(df["Runs"].sum() for df in all_batting if "Runs" in df.columns))
    total_wickets = int(sum(df["Wkts"].sum() for df in all_bowling if "Wkts" in df.columns))
    total_records = sum(len(df) for df in all_batting)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_players:,}</div>
            <div class="stat-label">👤 Total Players</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_runs:,}</div>
            <div class="stat-label">🏃 Total Runs</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_wickets:,}</div>
            <div class="stat-label">🎯 Total Wickets</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_records:,}</div>
            <div class="stat-label">📋 Total Records</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🚀 What You Can Do")

    f1, f2, f3 = st.columns(3)
    features = [
        ("📊", "Dashboard", "Explore batting & bowling metrics with interactive charts across any format"),
        ("👤", "Player Analysis", "Deep-dive into any player's batting, bowling, and fielding statistics"),
        ("⚖️", "Compare Players", "Side-by-side comparison with radar charts and grouped bar charts"),
        ("🏆", "Leaderboards", "Top 20 players with medal rankings across all stat categories"),
        ("🌍", "Country Analytics", "Runs & wickets breakdown by country with pie charts"),
        ("🔍", "Search", "Search any player across all formats simultaneously"),
    ]
    cols = [f1, f2, f3, f1, f2, f3]
    for i, (icon, title, desc) in enumerate(features):
        with cols[i]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="fc-icon">{icon}</div>
                <div class="fc-title">{title}</div>
                <div class="fc-desc">{desc}</div>
            </div><br>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="cricket-card">
        <h3 style='color:#e8c547;'>🏏 Welcome to Cricket Analytics Dashboard</h3>
        <p style='color:#c8d8e8;'>
        This platform brings together comprehensive cricket statistics from ODI, T20, and Test cricket into one
        unified analytics experience. Whether you're tracking your favourite player's career, comparing legends
        head-to-head, or analysing country-level dominance — everything is just a click away.
        </p>
        <p style='color:#8ab4c8; font-size:0.85em;'>Navigate using the sidebar to explore all 8 sections of the dashboard.</p>
    </div>""", unsafe_allow_html=True)

# ============================================================
# PAGE: DASHBOARD
# ============================================================

elif page == "📊 Dashboard":
    st.title("📊 Dashboard")

    format_choice = st.selectbox("Select Format:", ["ODI", "T20", "Test"], key="dash_fmt")
    batting_df = get_batting_df(format_choice)
    bowling_df = get_bowling_df(format_choice)

    if batting_df is None or batting_df.empty:
        st.error(f"Cannot load {format_choice} batting data.")
        st.stop()

    st.markdown("#### 🏏 Batting Highlights")
    c1, c2, c3, c4 = st.columns(4)

    top_run_idx = batting_df["Runs"].idxmax() if "Runs" in batting_df.columns else None
    top_avg_idx = batting_df[batting_df["Ave"] > 0]["Ave"].idxmax() if "Ave" in batting_df.columns else None
    top_sr_idx = batting_df[batting_df["SR"] > 0]["SR"].idxmax() if "SR" in batting_df.columns else None

    with c1:
        if top_run_idx is not None:
            row = batting_df.loc[top_run_idx]
            st.metric("🏃 Top Run Scorer", clean_player_name(row["Player"])[:18], f"{int(row['Runs']):,} runs")
    with c2:
        if top_avg_idx is not None:
            row = batting_df.loc[top_avg_idx]
            st.metric("📈 Highest Average", clean_player_name(row["Player"])[:18], f"{row['Ave']:.2f}")
    with c3:
        if "100" in batting_df.columns:
            total_100 = int(batting_df["100"].sum())
            st.metric("💯 Total Centuries", f"{total_100:,}", "across all players")
    with c4:
        if top_sr_idx is not None:
            row = batting_df.loc[top_sr_idx]
            st.metric("⚡ Best Strike Rate", clean_player_name(row["Player"])[:18], f"{row['SR']:.1f}")

    st.markdown("#### 🎯 Bowling Highlights")
    b1, b2, b3, b4 = st.columns(4)

    if bowling_df is not None and not bowling_df.empty:
        top_wkt_idx = bowling_df["Wkts"].idxmax() if "Wkts" in bowling_df.columns else None
        eco_df = bowling_df[(bowling_df["Econ"] > 0) & (bowling_df["Wkts"] >= 10)]
        top_eco_idx = eco_df["Econ"].idxmin() if not eco_df.empty else None

        with b1:
            if top_wkt_idx is not None:
                row = bowling_df.loc[top_wkt_idx]
                st.metric("🎯 Top Wicket Taker", clean_player_name(row["Player"])[:18], f"{int(row['Wkts'])} wickets")
        with b2:
            if top_eco_idx is not None:
                row = bowling_df.loc[top_eco_idx]
                st.metric("💨 Best Economy", clean_player_name(row["Player"])[:18], f"{row['Econ']:.2f}")
        with b3:
            if "5" in bowling_df.columns:
                total_5w = int(bowling_df["5"].sum())
                st.metric("🌟 5-Wicket Hauls", f"{total_5w:,}", "across all bowlers")
        with b4:
            valid_avg = bowling_df[(bowling_df["Ave"] > 0) & (bowling_df["Wkts"] >= 20)]
            if not valid_avg.empty:
                idx = valid_avg["Ave"].idxmin()
                row = bowling_df.loc[idx]
                st.metric("🎖️ Best Bowl Average", clean_player_name(row["Player"])[:18], f"{row['Ave']:.2f}")

    st.markdown("---")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("📊 Top 10 Run Scorers")
        if "Runs" in batting_df.columns:
            top = batting_df.nlargest(10, "Runs")[["Player", "Runs"]].copy()
            top["Player"] = top["Player"].apply(clean_player_name)
            fig = px.bar(top, x="Runs", y="Player", orientation="h",
                         title=f"Top 10 Run Scorers — {format_choice}",
                         color="Runs", color_continuous_scale=["#2d5a8e", "#e8c547"])
            apply_theme(fig)
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        st.subheader("🎯 Top 10 Wicket Takers")
        if bowling_df is not None and "Wkts" in bowling_df.columns:
            top = bowling_df.nlargest(10, "Wkts")[["Player", "Wkts"]].copy()
            top["Player"] = top["Player"].apply(clean_player_name)
            fig = px.bar(top, x="Wkts", y="Player", orientation="h",
                         title=f"Top 10 Wicket Takers — {format_choice}",
                         color="Wkts", color_continuous_scale=["#2d5a8e", "#ff6b6b"])
            apply_theme(fig)
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE: PLAYER ANALYSIS
# ============================================================

elif page == "👤 Player Analysis":
    st.title("👤 Player Analysis")

    format_choice = st.selectbox("Select Format:", ["ODI", "T20", "Test"], key="pa_fmt")
    batting_df = get_batting_df(format_choice)

    if batting_df is None or batting_df.empty:
        st.error(f"Cannot load {format_choice} batting data.")
        st.stop()

    player_list = sorted(batting_df["Player"].astype(str).unique().tolist())
    player_name = st.selectbox("👤 Select Player", player_list, key="pa_player")

    player_batting = batting_df[batting_df["Player"] == player_name]
    if player_batting.empty:
        st.warning("Player not found in batting data.")
        st.stop()

    row = player_batting.iloc[0]
    country = extract_country(player_name)
    display_name = clean_player_name(player_name)

    st.markdown(f"""
    <div class="cricket-card">
        <h2 style='color:#e8c547; margin:0;'>{display_name}</h2>
        <p style='color:#8ab4c8; margin:4px 0 0 0;'>🌍 {country} &nbsp;|&nbsp; 📅 {row.get('Span','—')} &nbsp;|&nbsp; 🏏 {format_choice}</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab_bat, tab_bowl, tab_field = st.tabs(["🏏 Batting", "🎯 Bowling", "🧤 Fielding"])

    with tab_bat:
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("Matches", int(safe_val(row.get("Mat", 0))))
        with m2:
            st.metric("Runs", int(safe_val(row.get("Runs", 0))))
        with m3:
            st.metric("Average", f"{safe_val(row.get('Ave', 0)):.2f}")
        with m4:
            st.metric("Strike Rate", f"{safe_val(row.get('SR', 0)):.1f}")
        with m5:
            st.metric("Centuries", int(safe_val(row.get("100", 0))))

        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)

        with col_a:
            bar_metrics = ["Runs", "Ave", "SR", "100", "50"]
            bar_values = [safe_val(row.get(m, 0)) for m in bar_metrics]
            bar_df = pd.DataFrame({"Metric": bar_metrics, "Value": bar_values})
            fig_bar = px.bar(bar_df, x="Metric", y="Value",
                             title=f"{display_name} — Batting Metrics",
                             color="Metric",
                             color_discrete_sequence=["#e8c547", "#4da6ff", "#ff6b6b", "#51cf66", "#f59f00"])
            apply_theme(fig_bar)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_b:
            hundreds = safe_val(row.get("100", 0))
            fifties = safe_val(row.get("50", 0))
            if hundreds + fifties > 0:
                fig_pie = px.pie(
                    names=["Centuries (100)", "Half-Centuries (50)"],
                    values=[hundreds, fifties],
                    title=f"{display_name} — Milestones",
                    hole=0.45,
                    color_discrete_sequence=["#e8c547", "#4da6ff"],
                )
                apply_theme(fig_pie)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No century/fifty data available.")

    with tab_bowl:
        bowling_df = get_bowling_df(format_choice)
        if bowling_df is not None and not bowling_df.empty:
            p_bowl = bowling_df[bowling_df["Player"] == player_name]
            if not p_bowl.empty:
                brow = p_bowl.iloc[0]
                b1, b2, b3, b4, b5 = st.columns(5)
                with b1:
                    st.metric("Wickets", int(safe_val(brow.get("Wkts", 0))))
                with b2:
                    st.metric("Economy", f"{safe_val(brow.get('Econ', 0)):.2f}")
                with b3:
                    st.metric("Average", f"{safe_val(brow.get('Ave', 0)):.2f}")
                with b4:
                    st.metric("Strike Rate", f"{safe_val(brow.get('SR', 0)):.1f}")
                with b5:
                    st.metric("BBI", str(brow.get("BBI", "—")))

                st.markdown("<br>", unsafe_allow_html=True)
                bowl_metrics = ["Wkts", "Econ", "Ave", "SR"]
                bowl_values = [safe_val(brow.get(m, 0)) for m in bowl_metrics]
                bdf = pd.DataFrame({"Metric": bowl_metrics, "Value": bowl_values})
                fig_bowl = px.bar(bdf, x="Metric", y="Value",
                                  title=f"{display_name} — Bowling Metrics",
                                  color="Metric",
                                  color_discrete_sequence=["#ff6b6b", "#4da6ff", "#e8c547", "#51cf66"])
                apply_theme(fig_bowl)
                st.plotly_chart(fig_bowl, use_container_width=True)
            else:
                st.info(f"No bowling data available for {display_name} in {format_choice}.")
        else:
            st.info(f"Bowling dataset not loaded for {format_choice}.")

    with tab_field:
        fielding_df = get_fielding_df(format_choice)
        if fielding_df is not None and not fielding_df.empty:
            p_field = fielding_df[fielding_df["Player"] == player_name]
            if not p_field.empty:
                frow = p_field.iloc[0]
                f1, f2, f3 = st.columns(3)
                with f1:
                    st.metric("Total Dismissals", int(safe_val(frow.get("Dis", 0))))
                with f2:
                    st.metric("Catches", int(safe_val(frow.get("Ct", 0))))
                with f3:
                    st.metric("Stumpings", int(safe_val(frow.get("St", 0))))

                # Pie of Ct vs St
                ct = safe_val(frow.get("Ct", 0))
                st_ = safe_val(frow.get("St", 0))
                if ct + st_ > 0:
                    fig_f = px.pie(
                        names=["Catches", "Stumpings"],
                        values=[ct, st_],
                        title=f"{display_name} — Dismissal Breakdown",
                        hole=0.45,
                        color_discrete_sequence=["#4da6ff", "#e8c547"],
                    )
                    apply_theme(fig_f)
                    st.plotly_chart(fig_f, use_container_width=True)
            else:
                st.info(f"No fielding data available for {display_name} in {format_choice}.")
        else:
            st.info(f"Fielding dataset not loaded for {format_choice}.")

# ============================================================
# PAGE: COMPARE PLAYERS
# ============================================================

elif page == "⚖️ Compare Players":
    st.title("⚖️ Compare Players")

    format_choice = st.selectbox("Select Format:", ["ODI", "T20", "Test"], key="comp_fmt")
    batting_df = get_batting_df(format_choice)

    if batting_df is None or batting_df.empty:
        st.error(f"Cannot load {format_choice} batting data.")
        st.stop()

    player_list = sorted(batting_df["Player"].astype(str).unique().tolist())
    if len(player_list) < 2:
        st.warning("Not enough players to compare.")
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        player1 = st.selectbox("👤 Player 1", player_list, key="cp1")
    with col2:
        remaining = [p for p in player_list if p != player1]
        player2 = st.selectbox("👤 Player 2", remaining, key="cp2")

    p1_rows = batting_df[batting_df["Player"] == player1]
    p2_rows = batting_df[batting_df["Player"] == player2]

    if p1_rows.empty or p2_rows.empty:
        st.warning("Could not find stats for one or both players.")
        st.stop()

    row1 = p1_rows.iloc[0]
    row2 = p2_rows.iloc[0]
    n1 = clean_player_name(player1)
    n2 = clean_player_name(player2)

    # Comparison table
    st.markdown("#### 📋 Batting Comparison")
    metrics_list = ["Mat", "Inns", "Runs", "Ave", "SR", "100", "50"]
    comp_dict = {"Metric": metrics_list}
    comp_dict[n1] = [safe_val(row1.get(m, 0)) for m in metrics_list]
    comp_dict[n2] = [safe_val(row2.get(m, 0)) for m in metrics_list]
    comp_df = pd.DataFrame(comp_dict)
    st.dataframe(comp_df.set_index("Metric"), use_container_width=True)

    # Grouped bar chart
    st.markdown("#### 📊 Grouped Bar Comparison")
    bar_metrics = ["Runs", "Ave", "SR", "100", "50"]
    fig_bar = go.Figure(data=[
        go.Bar(name=n1, x=bar_metrics,
               y=[safe_val(row1.get(m, 0)) for m in bar_metrics],
               marker_color="#e8c547"),
        go.Bar(name=n2, x=bar_metrics,
               y=[safe_val(row2.get(m, 0)) for m in bar_metrics],
               marker_color="#4da6ff"),
    ])
    fig_bar.update_layout(barmode="group", title=f"{n1} vs {n2} — Batting Metrics")
    apply_theme(fig_bar)
    st.plotly_chart(fig_bar, use_container_width=True)

    # Radar chart
    st.markdown("#### 🕸️ Radar Chart")
    categories = ["Runs (scaled)", "Average", "Strike Rate", "Centuries", "Half Centuries"]
    max_runs = batting_df["Runs"].max() if "Runs" in batting_df.columns else 1
    max_runs = max_runs if max_runs > 0 else 1

    def scale_player(r):
        return [
            (safe_val(r.get("Runs", 0)) / max_runs) * 100,
            min(safe_val(r.get("Ave", 0)), 100),
            min(safe_val(r.get("SR", 0)), 200) / 2,
            min(safe_val(r.get("100", 0)) * 5, 100),
            min(safe_val(r.get("50", 0)) * 2, 100),
        ]

    p1_vals = scale_player(row1)
    p2_vals = scale_player(row2)

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=p1_vals + [p1_vals[0]],
        theta=categories + [categories[0]],
        fill="toself", name=n1,
        line_color="#e8c547", fillcolor="rgba(232,197,71,0.2)",
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=p2_vals + [p2_vals[0]],
        theta=categories + [categories[0]],
        fill="toself", name=n2,
        line_color="#4da6ff", fillcolor="rgba(77,166,255,0.2)",
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="#0d2137",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1e3a5f", linecolor="#2d5a8e"),
            angularaxis=dict(gridcolor="#1e3a5f", linecolor="#2d5a8e"),
        ),
        paper_bgcolor="#0a1628",
        font={"color": "#c8d8e8"},
        title=f"Radar: {n1} vs {n2}",
        height=500,
        margin=dict(l=60, r=60, t=60, b=40),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ============================================================
# PAGE: LEADERBOARDS
# ============================================================

elif page == "🏆 Leaderboards":
    st.title("🏆 Leaderboards")

    format_choice = st.selectbox("Select Format:", ["ODI", "T20", "Test"], key="lb_fmt")

    tab_bat, tab_bowl, tab_field = st.tabs(["🏏 Batting", "🎯 Bowling", "🧤 Fielding"])

    with tab_bat:
        batting_df = get_batting_df(format_choice)
        if batting_df is not None and not batting_df.empty and "Runs" in batting_df.columns:
            top20 = batting_df.nlargest(20, "Runs").copy().reset_index(drop=True)
            top20.insert(0, "Rank", top20.index + 1)
            top20["🏅"] = top20["Rank"].apply(medal)
            top20["Player"] = top20["Player"].astype(str)
            top20["Country"] = top20["Player"].apply(extract_country)
            top20["Player"] = top20["Player"].apply(clean_player_name)
            cols_to_show = ["Rank", "🏅", "Player", "Country", "Mat", "Runs", "Ave", "SR", "100", "50"]
            cols_to_show = [c for c in cols_to_show if c in top20.columns]
            st.dataframe(
                top20[cols_to_show],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn("Rank", width="small"),
                    "🏅": st.column_config.TextColumn("🏅", width="small"),
                    "Runs": st.column_config.NumberColumn("Runs", format="%d"),
                    "Ave": st.column_config.NumberColumn("Average", format="%.2f"),
                    "SR": st.column_config.NumberColumn("Strike Rate", format="%.1f"),
                }
            )
        else:
            st.info("Batting data not available.")

    with tab_bowl:
        bowling_df = get_bowling_df(format_choice)
        if bowling_df is not None and not bowling_df.empty and "Wkts" in bowling_df.columns:
            top20 = bowling_df.nlargest(20, "Wkts").copy().reset_index(drop=True)
            top20.insert(0, "Rank", top20.index + 1)
            top20["🏅"] = top20["Rank"].apply(medal)
            top20["Player"] = top20["Player"].astype(str)
            top20["Country"] = top20["Player"].apply(extract_country)
            top20["Player"] = top20["Player"].apply(clean_player_name)
            cols_to_show = ["Rank", "🏅", "Player", "Country", "Mat", "Wkts", "Ave", "Econ", "BBI"]
            cols_to_show = [c for c in cols_to_show if c in top20.columns]
            st.dataframe(
                top20[cols_to_show],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Wkts": st.column_config.NumberColumn("Wickets", format="%d"),
                    "Ave": st.column_config.NumberColumn("Average", format="%.2f"),
                    "Econ": st.column_config.NumberColumn("Economy", format="%.2f"),
                }
            )
        else:
            st.info("Bowling data not available.")

    with tab_field:
        fielding_df = get_fielding_df(format_choice)
        if fielding_df is not None and not fielding_df.empty and "Dis" in fielding_df.columns:
            top20 = fielding_df.nlargest(20, "Dis").copy().reset_index(drop=True)
            top20.insert(0, "Rank", top20.index + 1)
            top20["🏅"] = top20["Rank"].apply(medal)
            top20["Player"] = top20["Player"].astype(str)
            top20["Country"] = top20["Player"].apply(extract_country)
            top20["Player"] = top20["Player"].apply(clean_player_name)
            cols_to_show = ["Rank", "🏅", "Player", "Country", "Mat", "Dis", "Ct", "St"]
            cols_to_show = [c for c in cols_to_show if c in top20.columns]
            st.dataframe(
                top20[cols_to_show],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Dis": st.column_config.NumberColumn("Dismissals", format="%d"),
                    "Ct": st.column_config.NumberColumn("Catches", format="%d"),
                    "St": st.column_config.NumberColumn("Stumpings", format="%d"),
                }
            )
        else:
            st.info("Fielding data not available.")

# ============================================================
# PAGE: COUNTRY ANALYTICS
# ============================================================

elif page == "🌍 Country Analytics":
    st.title("🌍 Country Analytics")

    format_choice = st.selectbox("Select Format:", ["ODI", "T20", "Test"], key="ca_fmt")
    stat_type = st.radio("Stat Type:", ["Batting (Runs)", "Bowling (Wickets)"], horizontal=True)

    if stat_type == "Batting (Runs)":
        df = get_batting_df(format_choice)
        value_col = "Runs"
        label = "Total Runs"
    else:
        df = get_bowling_df(format_choice)
        value_col = "Wkts"
        label = "Total Wickets"

    if df is None or df.empty:
        st.error(f"Data not available for {format_choice}.")
        st.stop()

    if value_col not in df.columns:
        st.error(f"Column '{value_col}' not found.")
        st.stop()

    df = df.copy()
    df["Country"] = df["Player"].astype(str).apply(extract_country)
    country_stats = (
        df[df["Country"] != "Unknown"]
        .groupby("Country")[value_col]
        .sum()
        .reset_index()
        .rename(columns={value_col: label})
        .sort_values(label, ascending=False)
    )

    top15 = country_stats.head(15)

    col_a, col_b = st.columns(2)

    with col_a:
        fig_bar = px.bar(top15, x=label, y="Country", orientation="h",
                         title=f"Top 15 Countries — {label} ({format_choice})",
                         color=label,
                         color_continuous_scale=["#2d5a8e", "#e8c547"])
        apply_theme(fig_bar)
        fig_bar.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_b:
        fig_pie = px.pie(top15, names="Country", values=label,
                         title=f"Country Share — {label} ({format_choice})",
                         hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Set3)
        apply_theme(fig_pie)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("#### 📋 Country Summary Table")
    st.dataframe(
        country_stats.reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
        column_config={label: st.column_config.NumberColumn(label, format="%d")},
    )

# ============================================================
# PAGE: SEARCH
# ============================================================

elif page == "🔍 Search":
    st.title("🔍 Search Players")

    search_term = st.text_input("🔎 Enter player name to search:", placeholder="e.g. Kohli, Root, Warner...")
    fmt_filter = st.radio("Filter by Format:", ["All Formats", "ODI", "T20", "Test"], horizontal=True)

    if search_term.strip():
        formats_to_search = ["ODI", "T20", "Test"] if fmt_filter == "All Formats" else [fmt_filter]
        found_any = False

        for fmt in formats_to_search:
            batting_df = get_batting_df(fmt)
            bowling_df = get_bowling_df(fmt)
            fielding_df = get_fielding_df(fmt)

            if batting_df is None:
                continue

            matches = batting_df[
                batting_df["Player"].astype(str).str.contains(search_term, case=False, na=False)
            ]

            if matches.empty:
                continue

            found_any = True
            st.markdown(f"### 🏏 {fmt} Results ({len(matches)} player(s))")

            for _, row in matches.iterrows():
                pname = str(row["Player"])
                display = clean_player_name(pname)
                country = extract_country(pname)

                has_bowl = (
                    bowling_df is not None
                    and not bowling_df[bowling_df["Player"] == pname].empty
                )
                has_field = (
                    fielding_df is not None
                    and not fielding_df[fielding_df["Player"] == pname].empty
                )

                badges = "🏏 Batting"
                if has_bowl:
                    badges += " &nbsp;|&nbsp; 🎯 Bowling"
                if has_field:
                    badges += " &nbsp;|&nbsp; 🧤 Fielding"

                st.markdown(f"""
                <div class="cricket-card" style="text-align:left;">
                    <b style="color:#e8c547; font-size:1.1em;">{display}</b> &nbsp;
                    <span style="color:#8ab4c8; font-size:0.85em;">🌍 {country} | 📅 {row.get('Span','—')}</span><br>
                    <span style="color:#c8d8e8; font-size:0.85em;">
                        Matches: <b>{int(safe_val(row.get('Mat',0)))}</b> &nbsp;
                        Runs: <b>{int(safe_val(row.get('Runs',0))):,}</b> &nbsp;
                        Avg: <b>{safe_val(row.get('Ave',0)):.2f}</b> &nbsp;
                        100s: <b>{int(safe_val(row.get('100',0)))}</b>
                    </span><br>
                    <span style="color:#4da6ff; font-size:0.78em;">{badges}</span>
                </div>""", unsafe_allow_html=True)

        if not found_any:
            st.warning(f"No players found matching **'{search_term}'** in {fmt_filter}.")
    else:
        st.info("Type a player name above to search across all formats.")

# ============================================================
# PAGE: DOWNLOADS
# ============================================================

elif page == "📥 Downloads":
    st.title("📥 Download Data")

    col1, col2 = st.columns(2)
    with col1:
        format_choice = st.selectbox("Select Format:", ["ODI", "T20", "Test"], key="dl_fmt")
    with col2:
        data_type = st.radio("Select Data Type:", ["Batting", "Bowling", "Fielding"], horizontal=True)

    key_map = {
        "ODI":  {"Batting": "odi_batting",  "Bowling": "odi_bowling",  "Fielding": "odi_fielding"},
        "T20":  {"Batting": "t20_batting",  "Bowling": "t20_bowling",  "Fielding": "t20_fielding"},
        "Test": {"Batting": "test_batting", "Bowling": "test_bowling", "Fielding": "test_fielding"},
    }

    key = key_map[format_choice][data_type]
    df = DATA.get(key)

    if df is not None and not df.empty:
        st.success(f"✅ {format_choice} {data_type} — {len(df):,} records loaded")
        st.markdown("#### 👀 Preview (first 10 rows)")
        st.dataframe(df.head(10), use_container_width=True)

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        filename = f"{key}.csv"

        st.download_button(
            label=f"📥 Download {format_choice} {data_type} as CSV",
            data=csv_bytes,
            file_name=filename,
            mime="text/csv",
        )
    else:
        st.error(f"No {format_choice} {data_type} data available to download.")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#4a6a8a; font-size:0.78em; padding: 8px 0;'>
    🏏 Cricket Analytics Dashboard &nbsp;|&nbsp; Built with Streamlit &amp; Plotly &nbsp;|&nbsp; Data updated January 2026
</div>
""", unsafe_allow_html=True)
