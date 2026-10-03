from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "matches.csv"


def create_base_table(season_df, all_teams=None):
    """Tworzy podstawowe statystyki wszystkich drużyn w sezonie."""

    if all_teams is None:
        teams = sorted(
            set(season_df["home_team"])
            | set(season_df["away_team"])
        )
    else:
        teams = sorted(all_teams)

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


def h2h_matches_complete(season_df, teams):
    """
    Sprawdza, czy wszystkie drużyny z równą liczbą punktów
    rozegrały między sobą komplet bezpośrednich spotkań.

    W obecnym formacie Ekstraklasy każda para drużyn
    powinna rozegrać dwa mecze: mecz i rewanż.
    """

    for i, team_a in enumerate(teams):
        for team_b in teams[i + 1:]:

            matches = season_df[
                (
                    (season_df["home_team"] == team_a)
                    & (season_df["away_team"] == team_b)
                )
                |
                (
                    (season_df["home_team"] == team_b)
                    & (season_df["away_team"] == team_a)
                )
            ]

            if len(matches) < 2:
                return False

    return True


def sort_tied_group(group, season_df):
    """
    Rozstrzyga kolejność drużyn mających identyczną
    liczbę punktów.

    Jeżeli zainteresowane drużyny rozegrały między sobą
    komplet bezpośrednich spotkań, stosowana jest mini-tabela H2H.

    Jeżeli komplet bezpośrednich spotkań nie został jeszcze
    rozegrany, H2H jest pomijane i stosowane są kryteria ogólne.
    """

    teams = group["team"].tolist()

    use_h2h = h2h_matches_complete(
        season_df,
        teams
    )

    if use_h2h:

        h2h = create_h2h_table(
            season_df,
            teams
        )

        group = group.merge(
            h2h,
            on="team",
            how="left"
        )

        if len(group) == 2:
            sort_columns = [
                "h2h_points",
                "h2h_goal_difference",
                "goal_difference",
                "goals_for",
                "wins",
                "away_wins",
            ]

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

    else:

        sort_columns = [
            "goal_difference",
            "goals_for",
            "wins",
            "away_wins",
        ]

    return group.sort_values(
        by=sort_columns,
        ascending=False
    )


def create_league_table(df, season, all_teams=None):
    """
    Tworzy tabelę ligową dla wskazanego sezonu.

    Drużyny są najpierw grupowane według liczby punktów.
    W przypadku remisu punktowego kolejność ustalana jest
    przez sort_tied_group().

    Dzięki temu H2H może zostać zastosowane również
    w trakcie sezonu, jeżeli zainteresowane drużyny
    rozegrały już komplet bezpośrednich spotkań.
    """

    season_df = df[
        df["season"] == season
    ].copy()

    table = create_base_table(
        season_df,
        all_teams=all_teams
    )

    sorted_groups = []

    # Najpierw grupujemy drużyny według liczby punktów.
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

    # Kolumny techniczne H2H nie są potrzebne
    # w finalnej tabeli prezentowanej użytkownikowi.
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


def create_team_progress(df, season, team):
    """
    Tworzy historię pozycji drużyny po każdym jej rozegranym meczu.

    Pozycja przedstawia stan tabeli na koniec dnia,
    w którym drużyna rozegrała dane spotkanie.
    """

    season_df = df[
        df["season"] == season
    ].copy()

    all_teams = sorted(
        set(season_df["home_team"])
        | set(season_df["away_team"])
    )

    team_matches = season_df[
        (season_df["home_team"] == team)
        | (season_df["away_team"] == team)
    ].copy()

    team_matches = team_matches.sort_values(
        by=["date", "time"]
    ).reset_index(drop=True)

    progress = []

    for match_number, (_, match) in enumerate(
        team_matches.iterrows(),
        start=1
    ):

        # Wszystkie mecze ligi rozegrane do dnia
        # danego spotkania włącznie.
        matches_so_far = season_df[
            season_df["date"] <= match["date"]
        ].copy()

        # Tabela ligowa na koniec danego dnia.
        table = create_league_table(
            matches_so_far,
            season,
            all_teams=all_teams
        )

        team_row = table[
            table["team"] == team
        ]

        if team_row.empty:
            continue

        team_row = team_row.iloc[0]

        # Informacje o konkretnym meczu.
        if match["home_team"] == team:
            opponent = match["away_team"]
            venue = "Dom"
            goals_for = int(match["home_goals"])
            goals_against = int(match["away_goals"])
            points = int(match["home_points"])
        else:
            opponent = match["home_team"]
            venue = "Wyjazd"
            goals_for = int(match["away_goals"])
            goals_against = int(match["home_goals"])
            points = int(match["away_points"])

        if points == 3:
            result = "W"
        elif points == 1:
            result = "R"
        else:
            result = "L"

        progress.append({
            "match_number": match_number,
            "date": match["date"],
            "opponent": opponent,
            "venue": venue,
            "score": f"{goals_for}:{goals_against}",
            "result": result,
            "points": points,
            "cumulative_points": int(team_row["points"]),
            "position": int(team_row["position"]),
        })

    return pd.DataFrame(progress)