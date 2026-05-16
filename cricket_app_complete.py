import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="🏏 Cricket Player Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================
# DATA CLEANING HELPERS
# ============================================

GENERIC_NUMERIC_COLS = [
    "Mat", "Inns", "NO", "Runs", "HS", "Ave", "BF", "SR",
    "100", "50", "0", "Balls", "Wkts", "Econ", "4", "5",
    "10", "Overs", "Ct", "St", "Dis",
]


def _strip_columns_and_strings(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip()
    obj_cols = df.select_dtypes(include=["object"]).columns
    for col in obj_cols:
        df[col] = df[col].astype(str).str.strip()
    return df


def _convert_numeric_columns(df: pd.DataFrame, numeric_cols) -> pd.DataFrame:
    df = df.copy()
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _fill_missing_numeric(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
    return df


def clean_for_app(df: pd.DataFrame) -> pd.DataFrame:
    """Light cleaning for use inside the app."""
    df = _strip_columns_and_strings(df)
    df = _convert_numeric_columns(df, GENERIC_NUMERIC_COLS)
    df = _fill_missing_numeric(df)
    return df


# Safe metric helpers
def safe_idx(df: pd.DataFrame, col: str, func) -> int | None:
    if col not in df.columns or df[col].dropna().empty:
        return None
    try:
        return func(df[col])
    except ValueError:
        return None


def safe_metric_label(df: pd.DataFrame, idx: int | None, label_col: str = "Player") -> str:
    if idx is None or label_col not in df.columns:
        return "N/A"
    try:
        return str(df.iloc[idx][label_col])[:20]
    except Exception:
        return "N/A"


def safe_metric_value(df: pd.DataFrame, col: str, fmt: str) -> str:
    if col not in df.columns or df[col].dropna().empty:
        return "N/A"
    try:
        return fmt.format(df[col].max())
    except Exception:
        return "N/A"


# ============================================
# LOAD AND CACHE DATA
# ============================================

@st.cache_data
def load_cricket_data():
    """Load and lightly clean cricket data from CSV files."""
    base = Path(".")
    try:
        odi_batting = clean_for_app(pd.read_csv(base / "odi_batting.csv"))
        odi_bowling = clean_for_app(pd.read_csv(base / "odi_bowling.csv"))
        odi_fielding = clean_for_app(pd.read_csv(base / "odi_fielding.csv"))

        t20_batting = clean_for_app(pd.read_csv(base / "t20_batting.csv"))
        t20_bowling = clean_for_app(pd.read_csv(base / "t20_bowling.csv"))
        t20_fielding = clean_for_app(pd.read_csv(base / "t20_fielding.csv"))

        test_batting = clean_for_app(pd.read_csv(base / "test_batting.csv"))
        test_bowling = clean_for_app(pd.read_csv(base / "test_bowling.csv"))
        test_fielding = clean_for_app(pd.read_csv(base / "test_fielding.csv"))

        return {
            "odi": {"batting": odi_batting, "bowling": odi_bowling, "fielding": odi_fielding},
            "t20": {"batting": t20_batting, "bowling": t20_bowling, "fielding": t20_fielding},
            "test": {"batting": test_batting, "bowling": test_bowling, "fielding": test_fielding},
        }
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.info("📁 Make sure all 9 CSV files are in the same folder as this app")
        return None


data = load_cricket_data()

if data is None:
    st.error("Could not load cricket data. Please check your CSV files.")
    st.stop()

# ============================================
# CUSTOM STYLING
# ============================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.5em;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================
# SIDEBAR NAVIGATION
# ============================================

st.sidebar.title("🏏 Cricket Analytics")
st.sidebar.write("---")

page = st.sidebar.radio(
    "Select Page",
    ["🏠 Home", "📊 Dashboard", "👤 Player Analysis", "⚖️ Comparison", "📈 Stats Lookup", "📋 About"],
)

st.sidebar.write("---")
st.sidebar.info("💡 Tip: Use the dropdown menus to select formats and categories")

# ============================================
# PAGE 1: HOME
# ============================================

if page == "🏠 Home":
    st.markdown('<div class="main-title">🏏 Cricket Player Analytics System</div>', unsafe_allow_html=True)

    st.write("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 Total Formats", 3, "ODI, T20, Test")
    with col2:
        st.metric("📊 Categories", 3, "Batting, Bowling, Fielding")
    with col3:
        st.metric("🎯 Data Types", 9, "All Formats")

    st.write("---")

    st.subheader("✨ Available Features")

    col1, col2 = st.columns(2)
    with col1:
        st.success(
            """
            ✅ **Batting Analysis**
            • Best Players Ranking
            • Most Runs Scorers
            • Century Records
            • 50-Run Landmarks
            • Player Search
            """
        )
    with col2:
        st.success(
            """
            ✅ **Bowling Analysis**
            • Best Bowlers Ranking
            • Most Wickets Takers
            • Best Economy Rate
            • Bowling Records
            • Player Search
            """
        )

    col3, col4 = st.columns(2)
    with col3:
        st.info(
            """
            ℹ️ **Fielding Analysis**
            • Most Catches
            • Most Stumpings
            • Fielding Comparisons
            • Player Search
            """
        )
    with col4:
        st.info(
            """
            ℹ️ **Comparison Tool**
            • Compare Multiple Players
            • Side-by-Side Stats
            • Visual Charts
            • Download Data
            """
        )

    st.write("---")
    st.success("👉 **Select a page from the sidebar to explore cricket analytics!**")

# ============================================
# PAGE 2: DASHBOARD
# ============================================

elif page == "📊 Dashboard":
    st.title("📊 Dashboard")

    format_choice = st.selectbox("📋 Select Format", ["ODI", "T20", "Test"])
    format_key = format_choice.lower()

    st.write("---")

    # BATTING DASHBOARD
    st.subheader("🏏 Batting Statistics")

    batting_df = data[format_key]["batting"].copy()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        idx = safe_idx(batting_df, "Runs", lambda s: s.idxmax())
        top_runner = safe_metric_label(batting_df, idx)
        top_runs = safe_metric_value(batting_df, "Runs", "{:.0f}")
        st.metric("🏃 Top Run Scorer", top_runner, f"{top_runs} runs")

    with col2:
        idx = safe_idx(batting_df, "100", lambda s: s.idxmax())
        century_maker = safe_metric_label(batting_df, idx)
        centuries = safe_metric_value(batting_df, "100", "{:.0f}")
        st.metric("💯 Most Centuries", century_maker, f"{centuries} centuries")

    with col3:
        idx = safe_idx(batting_df, "Ave", lambda s: s.idxmax())
        top_avg = safe_metric_label(batting_df, idx)
        avg_val = safe_metric_value(batting_df, "Ave", "{:.2f}")
        st.metric("📈 Highest Average", top_avg, avg_val)

    with col4:
        idx = safe_idx(batting_df, "50", lambda s: s.idxmax())
        fifty_maker = safe_metric_label(batting_df, idx)
        fifties = safe_metric_value(batting_df, "50", "{:.0f}")
        st.metric("5️⃣ Most Fifties", fifty_maker, f"{fifties} fifties")

    st.write("---")

    # BATTING CHARTS
    col1, col2 = st.columns(2)

    with col1:
        if "Runs" in batting_df.columns:
            top_runs_df = batting_df.nlargest(10, "Runs")[["Player", "Runs"]].copy()
            fig = px.bar(
                top_runs_df,
                x="Player",
                y="Runs",
                title=f"🏏 Top 10 Run Scorers - {format_choice}",
                color="Runs",
                color_continuous_scale="Blues",
            )
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "100" in batting_df.columns:
            top_centuries = batting_df.nlargest(10, "100")[["Player", "100"]].copy()
            fig = px.bar(
                top_centuries,
                x="Player",
                y="100",
                title=f"💯 Top 10 Century Makers - {format_choice}",
                color="100",
                color_continuous_scale="Greens",
            )
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    # NEW: PIE CHARTS FOR BATTING
    st.write("---")
    st.subheader("📊 Batting Distributions")

    pie_col1, pie_col2 = st.columns(2)

    with pie_col1:
        if "Runs" in batting_df.columns:
            top_runs_df = batting_df.nlargest(8, "Runs")[["Player", "Runs"]].copy()
            if not top_runs_df.empty:
                pie_fig = px.pie(
                    top_runs_df,
                    names="Player",
                    values="Runs",
                    title=f"🥧 Runs Share (Top 8) - {format_choice}",
                    hole=0.3,
                )
                st.plotly_chart(pie_fig, use_container_width=True)

    with pie_col2:
        if "100" in batting_df.columns:
            top_centuries_df = batting_df.nlargest(8, "100")[["Player", "100"]].copy()
            if not top_centuries_df.empty and top_centuries_df["100"].sum() > 0:
                pie_fig2 = px.pie(
                    top_centuries_df,
                    names="Player",
                    values="100",
                    title=f"🥧 Centuries Share (Top 8) - {format_choice}",
                    hole=0.3,
                )
                st.plotly_chart(pie_fig2, use_container_width=True)

    st.write("---")

    # BOWLING DASHBOARD
    st.subheader("🎯 Bowling Statistics")

    bowling_df = data[format_key]["bowling"].copy()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        idx = safe_idx(bowling_df, "Wkts", lambda s: s.idxmax())
        wicket_taker = safe_metric_label(bowling_df, idx)
        wickets = safe_metric_value(bowling_df, "Wkts", "{:.0f}")
        st.metric("🎯 Most Wickets", wicket_taker, f"{wickets} wickets")

    with col2:
        idx = safe_idx(bowling_df, "Ave", lambda s: s.idxmin())
        best_avg = safe_metric_label(bowling_df, idx)
        avg_val = safe_metric_value(bowling_df, "Ave", "{:.2f}")
        st.metric("📊 Best Average", best_avg, avg_val)

    with col3:
        idx = safe_idx(bowling_df, "Econ", lambda s: s.idxmin())
        econ_bowler = safe_metric_label(bowling_df, idx)
        econ_val = safe_metric_value(bowling_df, "Econ", "{:.2f}")
        st.metric("⚡ Best Economy", econ_bowler, econ_val)

    with col4:
        idx = safe_idx(bowling_df, "5", lambda s: s.idxmax())
        haul_bowler = safe_metric_label(bowling_df, idx)
        hauls = safe_metric_value(bowling_df, "5", "{:.0f}")
        st.metric("🏆 Most 5W Hauls", haul_bowler, hauls)

    col1, col2 = st.columns(2)

    with col1:
        if "Wkts" in bowling_df.columns:
            top_wickets = bowling_df.nlargest(10, "Wkts")[["Player", "Wkts"]].copy()
            fig = px.bar(
                top_wickets,
                x="Player",
                y="Wkts",
                title=f"🎯 Top 10 Wicket Takers - {format_choice}",
                color="Wkts",
                color_continuous_scale="Reds",
            )
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "Econ" in bowling_df.columns:
            best_econ = bowling_df.nsmallest(10, "Econ")[["Player", "Econ"]].copy()
            fig = px.bar(
                best_econ,
                x="Player",
                y="Econ",
                title=f"⚡ Best Economy Rates - {format_choice}",
                color="Econ",
                color_continuous_scale="Oranges",
            )
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    # NEW: PIE CHARTS FOR BOWLING
    st.write("---")
    st.subheader("📊 Bowling Distributions")

    bowl_pie_col1, bowl_pie_col2 = st.columns(2)

    with bowl_pie_col1:
        if "Wkts" in bowling_df.columns:
            top_wkts_df = bowling_df.nlargest(8, "Wkts")[["Player", "Wkts"]].copy()
            if not top_wkts_df.empty and top_wkts_df["Wkts"].sum() > 0:
                pie_fig3 = px.pie(
                    top_wkts_df,
                    names="Player",
                    values="Wkts",
                    title=f"🥧 Wickets Share (Top 8) - {format_choice}",
                    hole=0.3,
                )
                st.plotly_chart(pie_fig3, use_container_width=True)

    with bowl_pie_col2:
        if "5" in bowling_df.columns:
            top_5w_df = bowling_df.nlargest(8, "5")[["Player", "5"]].copy()
            if not top_5w_df.empty and top_5w_df["5"].sum() > 0:
                pie_fig4 = px.pie(
                    top_5w_df,
                    names="Player",
                    values="5",
                    title=f"🥧 5W Hauls Share (Top 8) - {format_choice}",
                    hole=0.3,
                )
                st.plotly_chart(pie_fig4, use_container_width=True)

# ============================================
# PAGE 3: PLAYER ANALYSIS
# ============================================

elif page == "👤 Player Analysis":
    st.title("👤 Individual Player Analysis")

    col1, col2 = st.columns(2)
    with col1:
        format_choice = st.selectbox("📋 Select Format", ["ODI", "T20", "Test"], key="analysis_format")
    with col2:
        analysis_type = st.selectbox("📊 Select Type", ["Batting", "Bowling", "Fielding"])

    format_key = format_choice.lower()
    type_key = analysis_type.lower()

    df = data[format_key][type_key].copy()

    if "Player" not in df.columns or df.empty:
        st.warning("No player data available for this selection.")
    else:
        player_name = st.selectbox("👤 Select Player", sorted(df["Player"].unique()))
        if player_name:
            player_row = df[df["Player"] == player_name]
            if player_row.empty:
                st.warning("No data for selected player.")
            else:
                player_data = player_row.iloc[0]
                st.write("---")

                if analysis_type == "Batting":
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🏃 Runs", f"{player_data.get('Runs', 0):.0f}")
                    with col2:
                        st.metric("📈 Average", f"{player_data.get('Ave', 0):.2f}")
                    with col3:
                        st.metric("💯 Centuries", f"{player_data.get('100', 0):.0f}")
                    with col4:
                        st.metric("5️⃣ Fifties", f"{player_data.get('50', 0):.0f}")

                    st.write("---")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🎯 Matches", f"{player_data.get('Mat', 0):.0f}")
                    with col2:
                        st.metric("🏏 Innings", f"{player_data.get('Inns', 0):.0f}")
                    with col3:
                        st.metric("⚡ Strike Rate", f"{player_data.get('SR', 0):.2f}")
                    with col4:
                        st.metric("🎪 Highest Score", f"{player_data.get('HS', 0)}")

                    st.write("---")

                    # BAR CHART
                    metrics = ["Runs", "Ave", "100", "50"]
                    values = [
                        player_data.get("Runs", 0),
                        player_data.get("Ave", 0),
                        player_data.get("100", 0),
                        player_data.get("50", 0),
                    ]

                    fig = go.Figure(
                        data=[
                            go.Bar(
                                x=metrics,
                                y=values,
                                marker=dict(
                                    color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
                                ),
                            )
                        ]
                    )
                    fig.update_layout(
                        title=f"🏏 {player_name} - Batting Stats ({format_choice})", height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # NEW: PIE CHART FOR PLAYER BATTING CONTRIBUTIONS
                    st.write("---")
                    st.subheader("🥧 Batting Contributions Breakdown")
                    pie_labels = ["Centuries (100s)", "Fifties (50s)"]
                    pie_values = [
                        player_data.get("100", 0),
                        player_data.get("50", 0),
                    ]
                    if sum(pie_values) > 0:
                        pie_fig = px.pie(
                            names=pie_labels,
                            values=pie_values,
                            title=f"{player_name} - 100s vs 50s",
                            hole=0.3,
                        )
                        st.plotly_chart(pie_fig, use_container_width=True)

                elif analysis_type == "Bowling":
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🎯 Wickets", f"{player_data.get('Wkts', 0):.0f}")
                    with col2:
                        st.metric("📊 Average", f"{player_data.get('Ave', 0):.2f}")
                    with col3:
                        st.metric("⚡ Economy", f"{player_data.get('Econ', 0):.2f}")
                    with col4:
                        st.metric("🏆 5W Hauls", f"{player_data.get('5', 0):.0f}")

                    st.write("---")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🎯 Matches", f"{player_data.get('Mat', 0):.0f}")
                    with col2:
                        st.metric("⚽ Strike Rate", f"{player_data.get('SR', 0):.2f}")
                    with col3:
                        st.metric("📈 4W Hauls", f"{player_data.get('4', 0):.0f}")

                    st.write("---")

                    metrics = ["Wkts", "Ave", "Econ", "5"]
                    values = [
                        player_data.get("Wkts", 0),
                        player_data.get("Ave", 0),
                        player_data.get("Econ", 0),
                        player_data.get("5", 0),
                    ]

                    fig = go.Figure(
                        data=[
                            go.Bar(
                                x=metrics,
                                y=values,
                                marker=dict(
                                    color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
                                ),
                            )
                        ]
                    )
                    fig.update_layout(
                        title=f"🎯 {player_name} - Bowling Stats ({format_choice})", height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # NEW: PIE CHART FOR 4W VS 5W
                    st.write("---")
                    st.subheader("🥧 Hauls Breakdown")
                    pie_labels = ["4-Wicket Hauls", "5-Wicket Hauls"]
                    pie_values = [
                        player_data.get("4", 0),
                        player_data.get("5", 0),
                    ]
                    if sum(pie_values) > 0:
                        pie_fig = px.pie(
                            names=pie_labels,
                            values=pie_values,
                            title=f"{player_name} - 4W vs 5W Hauls",
                            hole=0.3,
                        )
                        st.plotly_chart(pie_fig, use_container_width=True)

                elif analysis_type == "Fielding":
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("👐 Catches", f"{player_data.get('Ct', 0):.0f}")
                    with col2:
                        st.metric("🧤 Stumpings", f"{player_data.get('St', 0):.0f}")
                    with col3:
                        st.metric("🎯 Matches", f"{player_data.get('Mat', 0):.0f}")

                    st.write("---")

                    metrics = ["Catches", "Stumpings"]
                    values = [player_data.get("Ct", 0), player_data.get("St", 0)]

                    fig = go.Figure(
                        data=[
                            go.Bar(
                                x=metrics,
                                y=values,
                                marker=dict(color=["#1f77b4", "#ff7f0e"]),
                            )
                        ]
                    )
                    fig.update_layout(
                        title=f"🧤 {player_name} - Fielding Stats ({format_choice})", height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # NEW: PIE CHART FOR CATCHES VS STUMPINGS
                    st.write("---")
                    st.subheader("🥧 Fielding Contributions")
                    if sum(values) > 0:
                        pie_fig = px.pie(
                            names=metrics,
                            values=values,
                            title=f"{player_name} - Catches vs Stumpings",
                            hole=0.3,
                        )
                        st.plotly_chart(pie_fig, use_container_width=True)

# ============================================
# PAGE 4: COMPARISON
# ============================================

elif page == "⚖️ Comparison":
    st.title("⚖️ Player Comparison")

    col1, col2 = st.columns(2)
    with col1:
        format_choice = st.selectbox("📋 Select Format", ["ODI", "T20", "Test"], key="compare_format")
    with col2:
        comparison_type = st.selectbox("📊 Select Type", ["Batting", "Bowling", "Fielding"])

    format_key = format_choice.lower()
    type_key = comparison_type.lower()

    df = data[format_key][type_key].copy()

    if "Player" not in df.columns or df.empty:
        st.warning("No player data available for this selection.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            player1 = st.selectbox(
                "👤 Select First Player", sorted(df["Player"].unique()), key="p1"
            )
        with col2:
            player2 = st.selectbox(
                "👤 Select Second Player", sorted(df["Player"].unique()), key="p2"
            )

        if player1 and player2 and player1 != player2:
            st.write("---")

            p1_row = df[df["Player"] == player1]
            p2_row = df[df["Player"] == player2]

            if p1_row.empty or p2_row.empty:
                st.warning("Data not found for one of the players.")
            else:
                p1_data = p1_row.iloc[0]
                p2_data = p2_row.iloc[0]

                if comparison_type == "Batting":
                    st.subheader(f"🏏 Batting Comparison: {player1} vs {player2}")

                    comparison_df = pd.DataFrame(
                        {
                            player1: [
                                p1_data.get("Runs", 0),
                                p1_data.get("Ave", 0),
                                p1_data.get("100", 0),
                                p1_data.get("50", 0),
                                p1_data.get("SR", 0),
                            ],
                            player2: [
                                p2_data.get("Runs", 0),
                                p2_data.get("Ave", 0),
                                p2_data.get("100", 0),
                                p2_data.get("50", 0),
                                p2_data.get("SR", 0),
                            ],
                        },
                        index=["Runs", "Average", "Centuries", "Fifties", "Strike Rate"],
                    )

                    st.dataframe(comparison_df, use_container_width=True)

                    fig = go.Figure(
                        data=[
                            go.Bar(
                                name=player1,
                                x=comparison_df.index,
                                y=comparison_df[player1],
                            ),
                            go.Bar(
                                name=player2,
                                x=comparison_df.index,
                                y=comparison_df[player2],
                            ),
                        ]
                    )
                    fig.update_layout(
                        barmode="group", title="🏏 Batting Comparison", height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # NEW: PIE CHART OF RUNS SHARE BETWEEN TWO PLAYERS
                    st.write("---")
                    st.subheader("🥧 Runs Share Between Players")
                    runs_share_df = pd.DataFrame(
                        {
                            "Player": [player1, player2],
                            "Runs": [p1_data.get("Runs", 0), p2_data.get("Runs", 0)],
                        }
                    )
                    if runs_share_df["Runs"].sum() > 0:
                        pie_fig = px.pie(
                            runs_share_df,
                            names="Player",
                            values="Runs",
                            title="Runs Contribution Share",
                            hole=0.3,
                        )
                        st.plotly_chart(pie_fig, use_container_width=True)

                elif comparison_type == "Bowling":
                    st.subheader(f"🎯 Bowling Comparison: {player1} vs {player2}")

                    comparison_df = pd.DataFrame(
                        {
                            player1: [
                                p1_data.get("Wkts", 0),
                                p1_data.get("Ave", 0),
                                p1_data.get("Econ", 0),
                                p1_data.get("5", 0),
                            ],
                            player2: [
                                p2_data.get("Wkts", 0),
                                p2_data.get("Ave", 0),
                                p2_data.get("Econ", 0),
                                p2_data.get("5", 0),
                            ],
                        },
                        index=["Wickets", "Average", "Economy", "5-Wick Hauls"],
                    )

                    st.dataframe(comparison_df, use_container_width=True)

                    fig = go.Figure(
                        data=[
                            go.Bar(
                                name=player1,
                                x=comparison_df.index,
                                y=comparison_df[player1],
                            ),
                            go.Bar(
                                name=player2,
                                x=comparison_df.index,
                                y=comparison_df[player2],
                            ),
                        ]
                    )
                    fig.update_layout(
                        barmode="group", title="🎯 Bowling Comparison", height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # NEW: PIE CHART OF WICKETS SHARE
                    st.write("---")
                    st.subheader("🥧 Wickets Share Between Players")
                    wickets_share_df = pd.DataFrame(
                        {
                            "Player": [player1, player2],
                            "Wkts": [p1_data.get("Wkts", 0), p2_data.get("Wkts", 0)],
                        }
                    )
                    if wickets_share_df["Wkts"].sum() > 0:
                        pie_fig = px.pie(
                            wickets_share_df,
                            names="Player",
                            values="Wkts",
                            title="Wickets Contribution Share",
                            hole=0.3,
                        )
                        st.plotly_chart(pie_fig, use_container_width=True)

                elif comparison_type == "Fielding":
                    st.subheader(f"🧤 Fielding Comparison: {player1} vs {player2}")

                    comparison_df = pd.DataFrame(
                        {
                            player1: [
                                p1_data.get("Ct", 0),
                                p1_data.get("St", 0),
                            ],
                            player2: [
                                p2_data.get("Ct", 0),
                                p2_data.get("St", 0),
                            ],
                        },
                        index=["Catches", "Stumpings"],
                    )

                    st.dataframe(comparison_df, use_container_width=True)

                    fig = go.Figure(
                        data=[
                            go.Bar(
                                name=player1,
                                x=comparison_df.index,
                                y=comparison_df[player1],
                            ),
                            go.Bar(
                                name=player2,
                                x=comparison_df.index,
                                y=comparison_df[player2],
                            ),
                        ]
                    )
                    fig.update_layout(
                        barmode="group", title="🧤 Fielding Comparison", height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # NEW: PIE CHART OF TOTAL DISMISSALS (Ct+St)
                    st.write("---")
                    st.subheader("🥧 Fielding Dismissals Share")
                    p1_dis = p1_data.get("Ct", 0) + p1_data.get("St", 0)
                    p2_dis = p2_data.get("Ct", 0) + p2_data.get("St", 0)
                    field_share_df = pd.DataFrame(
                        {"Player": [player1, player2], "Dismissals": [p1_dis, p2_dis]}
                    )
                    if field_share_df["Dismissals"].sum() > 0:
                        pie_fig = px.pie(
                            field_share_df,
                            names="Player",
                            values="Dismissals",
                            title="Total Fielding Dismissals Share",
                            hole=0.3,
                        )
                        st.plotly_chart(pie_fig, use_container_width=True)
        else:
            st.warning("⚠️ Please select two different players to compare")

# ============================================
# PAGE 5: STATS LOOKUP
# ============================================

elif page == "📈 Stats Lookup":
    st.title("📈 Statistics & Search")

    col1, col2 = st.columns(2)
    with col1:
        format_choice = st.selectbox("📋 Select Format", ["ODI", "T20", "Test"], key="lookup_format")
    with col2:
        lookup_type = st.selectbox("📊 Select Type", ["Batting", "Bowling", "Fielding"])

    format_key = format_choice.lower()
    type_key = lookup_type.lower()

    df = data[format_key][type_key].copy()

    st.write("---")

    search_name = st.text_input("🔍 Search Player Name (optional)")

    if "Player" not in df.columns or df.empty:
        st.warning("No player data available.")
    else:
        if search_name:
            filtered_df = df[df["Player"].str.contains(search_name, case=False, na=False)]
            if len(filtered_df) > 0:
                st.write(f"Found {len(filtered_df)} player(s)")
                st.dataframe(filtered_df, use_container_width=True)
                download_df = filtered_df
            else:
                st.warning("❌ No players found with that name")
                download_df = df
        else:
            st.write(f"Showing all {len(df)} players")
            st.dataframe(df, use_container_width=True)
            download_df = df

        st.write("---")

        csv = download_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"{format_key}_{lookup_type.lower()}_stats.csv",
            mime="text/csv",
        )

# ============================================
# PAGE 6: ABOUT
# ============================================

elif page == "📋 About":
    st.title("ℹ️ About Cricket Analytics")

    st.write(
        """
        ### 🏏 Cricket Player Analytics System

        This interactive web application provides comprehensive cricket statistics and analytics
        across multiple formats and categories.

        #### 📊 Formats Covered:
        - **ODI** (One Day International) - 50 overs per side
        - **T20** (Twenty20) - 20 overs per side
        - **Test** - 5 day format with unlimited overs

        #### 📈 Categories:
        - **Batting Statistics**: Runs, Averages, Centuries, Fifties, Strike Rate
        - **Bowling Statistics**: Wickets, Economy, Averages, Hauls
        - **Fielding Statistics**: Catches, Stumpings

        #### 🎯 Key Features:
        - ✅ Dashboard with top performers
        - ✅ Individual player analysis
        - ✅ Player comparison tool
        - ✅ Advanced search functionality
        - ✅ Data export to CSV
        - ✅ Interactive visualizations with Plotly
        - ✅ Real-time statistics

        #### 💡 How to Use:
        1. Select a format (ODI, T20, Test)
        2. Choose the category (Batting, Bowling, Fielding)
        3. Explore player statistics and comparisons
        4. Download data for further analysis
        5. Compare players side-by-side

        #### 🔧 Technology Stack:
        - **Framework**: Streamlit (Python)
        - **Data Processing**: Pandas, NumPy
        - **Visualization**: Plotly
        - **Language**: Python 3.9+

        #### 📝 Data Format:
        The app expects 9 CSV files:
        - odi_batting.csv, odi_bowling.csv, odi_fielding.csv
        - t20_batting.csv, t20_bowling.csv, t20_fielding.csv
        - test_batting.csv, test_bowling.csv, test_fielding.csv

        #### 🎓 Tips:
        - Use Dashboard for quick overview
        - Use Player Analysis for deep dive into stats
        - Use Comparison for side-by-side analysis
        - Use Stats Lookup to search and download data

        ---
        **Built with ❤️ for cricket enthusiasts**
        """
    )

    st.write("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("✅ Real-time Analysis")
    with col2:
        st.info("📱 Mobile Responsive")
    with col3:
        st.warning("🏆 Professional Grade")

# ============================================
# FOOTER
# ============================================

st.write("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    🏏 Cricket Player Analytics System | Built with Streamlit | 2026
    </div>
    """,
    unsafe_allow_html=True,
)
