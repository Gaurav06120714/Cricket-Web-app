# 🏏 Cricket Analytics Dashboard

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red?logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-lightblue?logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green)

A professional, dark-themed cricket analytics web application built with Streamlit and Plotly.  
Explore batting, bowling, and fielding statistics across **ODI**, **T20**, and **Test** cricket formats.

---

## Features

The app includes **8 fully functional pages**:

| Page | Description |
|------|-------------|
| 🏠 **Home** | Hero section with aggregated totals across all formats and feature overview |
| 📊 **Dashboard** | Format selector, 8 highlight metric cards, and top-10 horizontal bar charts |
| 👤 **Player Analysis** | Batting / Bowling / Fielding tabs for any player with charts and donut charts |
| ⚖️ **Compare Players** | Side-by-side stats table, grouped bar chart, and interactive radar chart |
| 🏆 **Leaderboards** | Top 20 players with 🥇🥈🥉 medals for batting, bowling, and fielding |
| 🌍 **Country Analytics** | Runs / wickets aggregated by country with bar and pie charts |
| 🔍 **Search** | Cross-format player search with batting/bowling/fielding availability badges |
| 📥 **Downloads** | Preview any dataset and download as CSV |

---

## Tech Stack

- **[Streamlit](https://streamlit.io/)** — web app framework
- **[Plotly](https://plotly.com/python/)** — interactive charts (bar, pie, donut, radar)
- **[Pandas](https://pandas.pydata.org/)** — data loading and transformation
- **[NumPy](https://numpy.org/)** — numerical helpers

---

## How to Run Locally

**1. Clone the repository and navigate to it:**
```bash
git clone https://github.com/Gaurav06120714/Cricket-Web-app.git
cd Cricket-Web-app
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Run the app:**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Project Structure

```
cricket-webapp/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── data_cleaning.py        # Standalone data cleaning utilities
├── cleaned_data/
│   ├── odi_batting.csv
│   ├── odi_bowling.csv
│   ├── odi_fielding.csv
│   ├── t20_batting.csv
│   ├── t20_bowling.csv
│   ├── t20_fielding.csv
│   ├── test_batting.csv
│   ├── test_bowling.csv
│   └── test_fielding.csv
└── README.md
```

---

## Screenshots

> _Screenshots coming soon._

---

## Data Sources

All data is stored in `cleaned_data/` as CSV files. Each file contains player-level statistics
scraped and cleaned from publicly available cricket records:

- **Batting:** Mat, Inns, NO, Runs, HS, Ave, BF, SR, 100, 50
- **Bowling:** Mat, Inns, Balls, Runs, Wkts, BBI, Ave, Econ, SR, 4w, 5w
- **Fielding:** Mat, Inns, Dis, Ct, St, Ct Wk, Ct Fi

Player names follow the format `Player Name (Country)` which the app parses automatically.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
