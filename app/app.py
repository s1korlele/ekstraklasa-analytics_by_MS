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
# Wybór drużyny
# --------------------------------------------------

# Drużyny występujące w aktualnie wybranym sezonie
season_teams = sorted(
    set(season_df["home_team"]) |
    set(season_df["away_team"])
)

# Pierwsze uruchomienie aplikacji
if "team_select" not in st.session_state:
    st.session_state.team_select = "Wszystkie drużyny"

# Aktualnie zapamiętana drużyna
previous_team = st.session_state.team_select

# Standardowo dropdown zawiera tylko drużyny
# występujące w wybranym sezonie
team_options = ["Wszystkie drużyny"] + season_teams

# Jeśli wcześniej wybrana drużyna nie grała w tym sezonie,
# tymczasowo zostawiamy ją jako dodatkową opcję
if (
    previous_team != "Wszystkie drużyny"
    and previous_team not in season_teams
):
    team_options.insert(1, previous_team)

# Selectbox sam przechowuje swój stan
selected_team = st.selectbox(
    "Wybierz drużynę",
    team_options,
    key="team_select",
)

# Sprawdzamy, czy wybrana drużyna grała w danym sezonie
team_in_season = (
    selected_team == "Wszystkie drużyny"
    or selected_team in season_teams
)

if (
    selected_team != "Wszystkie drużyny"
    and not team_in_season
):
    st.info(
        f"{selected_team} nie występował w Ekstraklasie "
        f"w sezonie {selected_season}. "
        f"Możesz wybrać inny sezon albo drużynę "
        f"występującą w tym sezonie."
    )

# --------------------------------------------------
# KPI
# --------------------------------------------------

if selected_team == "Wszystkie drużyny":

    # Statystyki całej ligi
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

else:

    # Statystyki wybranej drużyny pobieramy z tabeli ligowej
    team_table = create_league_table(
        df,
        selected_season
    )

    team_stats = team_table[
        team_table["team"] == selected_team
    ]

    if not team_stats.empty:

        team_stats = team_stats.iloc[0]

        matches = int(team_stats["matches"])
        wins = int(team_stats["wins"])
        draws = int(team_stats["draws"])
        losses = int(team_stats["losses"])
        goals_for = int(team_stats["goals_for"])
        goals_against = int(team_stats["goals_against"])
        goal_difference = int(team_stats["goal_difference"])
        points = int(team_stats["points"])

        goals_per_match = (
            goals_for / matches
            if matches > 0
            else 0
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Mecze",
            matches
        )

        col2.metric(
            "Punkty",
            points
        )

        col3.metric(
            "W / R / P",
            f"{wins} / {draws} / {losses}"
        )

        col4, col5, col6 = st.columns(3)

        col4.metric(
            "Gole",
            f"{goals_for}:{goals_against}"
        )

        col5.metric(
            "Bilans bramek",
            f"{goal_difference:+d}"
        )

        col6.metric(
            "Gole / mecz",
            f"{goals_per_match:.2f}"
        )

    else:

        st.info(
            "Brak statystyk drużyny dla wybranego sezonu."
        )
# --------------------------------------------------
# Tabela ligowa
# --------------------------------------------------

st.subheader("Tabela ligowa")

league_table = create_league_table(
    df,
    selected_season
)

if selected_team != "Wszystkie drużyny":
    league_table = league_table[
        league_table["team"] == selected_team
    ]

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

# --------------------------------------------------
# Ostatnie 5 meczów wybranej drużyny
# --------------------------------------------------

if selected_team != "Wszystkie drużyny" and team_in_season:

    st.subheader(f"Ostatnie 5 meczów — {selected_team}")

    team_matches = season_df[
        (season_df["home_team"] == selected_team) |
        (season_df["away_team"] == selected_team)
    ].copy()

    team_matches = team_matches.sort_values(
        by="date",
        ascending=False
    ).head(5)


    # Wynik meczu z perspektywy wybranej drużyny
    def get_form(row):

        if row["result"] == "D":
            return "R"

        if (
            row["home_team"] == selected_team
            and row["result"] == "H"
        ):
            return "W"

        if (
            row["away_team"] == selected_team
            and row["result"] == "A"
        ):
            return "W"

        return "L"


    team_matches["Forma"] = team_matches.apply(
        get_form,
        axis=1
    )

    # Data i godzina w jednym polu
    team_matches["Data"] = (
        team_matches["date"].dt.strftime("%d.%m.%Y")
        + " "
        + team_matches["time"].astype(str).str[:5]
    )

    # Rywal
    team_matches["Rywal"] = team_matches.apply(
        lambda row: (
            row["away_team"]
            if row["home_team"] == selected_team
            else row["home_team"]
        ),
        axis=1
    )

    # Miejsce rozegrania meczu
    team_matches["Miejsce"] = team_matches.apply(
        lambda row: (
            "Dom"
            if row["home_team"] == selected_team
            else "Wyjazd"
        ),
        axis=1
    )

    # Wynik z perspektywy wybranej drużyny
    team_matches["Wynik"] = team_matches.apply(
        lambda row: (
            f"{int(row['home_goals'])}:{int(row['away_goals'])}"
            if row["home_team"] == selected_team
            else f"{int(row['away_goals'])}:{int(row['home_goals'])}"
        ),
        axis=1
    )

    recent_matches = team_matches[
        [
            "Data",
            "Rywal",
            "Miejsce",
            "Wynik",
            "Forma",
        ]
    ].copy()

    # Kolory W / R / L
    def color_form(value):

        colors = {
            "W": "background-color: #198754; color: white",
            "R": "background-color: #6c757d; color: white",
            "L": "background-color: #dc3545; color: white",
        }

        return colors.get(value, "")


    st.dataframe(
        recent_matches.style.map(
            color_form,
            subset=["Forma"]
        ),
        hide_index=True,
        width="stretch",
    )