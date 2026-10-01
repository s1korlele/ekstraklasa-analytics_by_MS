from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "matches.csv"


def create_base_table(season_df):
    """Tworzy podstawowe statystyki wszystkich drużyn w sezonie."""

    teams = sorted(
        set(season_df["home_team"]) |
        set(season_df["away_team"])
    )

    table = []

    for team in teams:
        home = season_df[season_df["home_team"] == team]
        away = season_df[season_df["away_team"] == team]

        matches = len(home) + len(away)

        wins = (
            (home["result"] == "H").sum()
            + (away["result"] == "A").sum()
        )

        draws = (
            (home["result"] == "D").sum()
            + (away["result"] == "D").sum()
        )

        losses = matches - wins - draws

        goals_for = (
            home["home_goals"].sum()
            + away["away_goals"].sum()
        )

        goals_against = (
            home["away_goals"].sum()
            + away["home_goals"].sum()
        )

        points = (
            home["home_points"].sum()
            + away["away_points"].sum()
        )

        away_wins = (away["result"] == "A").sum()

        table.append({
            "team": team,
            "matches": matches,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_difference": goals_for - goals_against,
            "points": points,
            "away_wins": away_wins,
        })

    return pd.DataFrame(table)


def create_h2h_table(season_df, teams):
    """
    Tworzy mini-tabelę wyłącznie z meczów rozegranych
    pomiędzy wskazanymi drużynami.
    """

    h2h_matches = season_df[
        season_df["home_team"].isin(teams)
        & season_df["away_team"].isin(teams)
    ]

    records = []

    for team in teams:
        home = h2h_matches[h2h_matches["home_team"] == team]
        away = h2h_matches[h2h_matches["away_team"] == team]

        h2h_points = (
            home["home_points"].sum()
            + away["away_points"].sum()
        )

        h2h_goals_for = (
            home["home_goals"].sum()
            + away["away_goals"].sum()
        )

        h2h_goals_against = (
            home["away_goals"].sum()
            + away["home_goals"].sum()
        )

        records.append({
            "team": team,
            "h2h_points": h2h_points,
            "h2h_goal_difference":
                h2h_goals_for - h2h_goals_against,
            "h2h_goals_for": h2h_goals_for,
        })

    return pd.DataFrame(records)


def sort_tied_group(group, season_df):
    """
    Rozstrzyga kolejność drużyn mających
    identyczną liczbę punktów.
    """

    teams = group["team"].tolist()

    h2h = create_h2h_table(
        season_df,
        teams
    )

    group = group.merge(
        h2h,
        on="team",
        how="left"
    )

    # Przy dwóch drużynach regulamin nie używa liczby goli H2H jako osobnego kryterium.
    if len(group) == 2:
        sort_columns = [
            "h2h_points",
            "h2h_goal_difference",
            "goal_difference",
            "goals_for",
            "wins",
            "away_wins",
        ]

    # Przy 3+ drużynach wykorzystujemy mini-tabelę, w tym gole zdobyte H2H.
    else:
        sort_columns = [
            "h2h_points",
            "h2h_goal_difference",
            "h2h_goals_for",
            "goal_difference",
            "goals_for",
            "wins",
            "away_wins",
        ]

    return group.sort_values(
        by=sort_columns,
        ascending=False
    )


def create_league_table(df, season):

    season_df = df[
        df["season"] == season
    ].copy()

    table = create_base_table(season_df)

    sorted_groups = []

    # Najpierw punkty całego sezonu.
    # Każdą grupę z równą liczbą punktów rozstrzygamy osobno.
    for points in sorted(
        table["points"].unique(),
        reverse=True
    ):
        group = table[
            table["points"] == points
        ].copy()

        if len(group) > 1:
            group = sort_tied_group(
                group,
                season_df
            )

        sorted_groups.append(group)

    table = pd.concat(
        sorted_groups,
        ignore_index=True
    )

    table.insert(
        0,
        "position",
        range(1, len(table) + 1)
    )

    # Kolumny techniczne H2H nie są potrzebne w finalnej tabeli.
    h2h_columns = [
        "h2h_points",
        "h2h_goal_difference",
        "h2h_goals_for",
    ]

    table = table.drop(
        columns=[
            column
            for column in h2h_columns
            if column in table.columns
        ]
    )

    return table


if __name__ == "__main__":

    df = pd.read_csv(DATA_PATH)

    table = create_league_table(
        df,
        season="2024/2025"
    )

    print("\n=== EKSTRAKLASA 2024/2025 ===\n")

    print(
        table.to_string(
            index=False
        )
    )