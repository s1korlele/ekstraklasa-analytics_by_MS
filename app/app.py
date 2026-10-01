from pathlib import Path
import sys

import pandas as pd
import streamlit as st


# --------------------------------------------------
# Ścieżki projektu
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.append(str(PROJECT_ROOT))

from src.league_table import create_league_table


DATA_PATH = PROJECT_ROOT / "data" / "processed" / "matches.csv"


# --------------------------------------------------
# Konfiguracja aplikacji
# --------------------------------------------------

st.set_page_config(
    page_title="Ekstraklasa Analytics",
    page_icon="⚽",
    layout="wide",
)


# --------------------------------------------------
# Wczytanie danych
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])

    return df


df = load_data()


# --------------------------------------------------
# Nagłówek
# --------------------------------------------------

st.title("⚽ Ekstraklasa Analytics")

st.caption(
    "Interaktywny dashboard wyników i statystyk "
    "polskiej Ekstraklasy."
)


# --------------------------------------------------
# Wybór sezonu
# --------------------------------------------------

seasons = sorted(
    df["season"].unique(),
    reverse=True
)

selected_season = st.selectbox(
    "Wybierz sezon",
    seasons
)


season_df = df[
    df["season"] == selected_season
].copy()


# --------------------------------------------------
# KPI
# --------------------------------------------------

matches = len(season_df)

total_goals = (
    season_df["home_goals"].sum()
    + season_df["away_goals"].sum()
)

goals_per_match = (
    total_goals / matches
    if matches > 0
    else 0
)


col1, col2, col3 = st.columns(3)

col1.metric(
    "Mecze",
    matches
)

col2.metric(
    "Gole",
    int(total_goals)
)

col3.metric(
    "Gole / mecz",
    f"{goals_per_match:.2f}"
)


# --------------------------------------------------
# Tabela ligowa
# --------------------------------------------------

st.subheader("Tabela ligowa")

league_table = create_league_table(
    df,
    selected_season
)

display_table = league_table[
    [
        "position",
        "team",
        "matches",
        "wins",
        "draws",
        "losses",
        "goals_for",
        "goals_against",
        "goal_difference",
        "points",
    ]
].copy()


display_table.columns = [
    "Poz.",
    "Drużyna",
    "M",
    "W",
    "R",
    "P",
    "BZ",
    "BS",
    "RB",
    "Pkt",
]


st.dataframe(
    display_table,
    hide_index=True,
    width="stretch",
)