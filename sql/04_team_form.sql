/*
    File: 04_team_form.sql
    Database: PostgreSQL 18
    Schema: public
    Source table: public.matches

    Purpose:
    Analyse each team's form throughout an Ekstraklasa season.

    Every fixture is transformed into two team-level observations.
    Window functions are then used to calculate the team's chronological
    match number and rolling performance over its last five matches.

    The rolling window includes the current match and the four immediately
    preceding matches played by the same team in the same season.

    In addition to numerical rolling metrics, last_5_form provides a compact
    representation of recent results, for example: WDWLL.

    Important:
    The source dataset does not contain official matchday numbers.
    Therefore, match_number represents the chronological number of a match
    played by a specific team, not an official league round.
*/


-- ============================================================
-- 1. Transform fixtures into team-level observations
-- ============================================================

WITH team_matches AS (

    -- Home team's perspective
    SELECT
        season,
        date,
        time,
        home_team AS team,
        away_team AS opponent,
        'home' AS venue,
        home_goals AS goals_for,
        away_goals AS goals_against,
        home_points AS points
    FROM public.matches

    UNION ALL

    -- Away team's perspective
    SELECT
        season,
        date,
        time,
        away_team AS team,
        home_team AS opponent,
        'away' AS venue,
        away_goals AS goals_for,
        home_goals AS goals_against,
        away_points AS points
    FROM public.matches
),


-- ============================================================
-- 2. Order matches chronologically for each team and season
-- ============================================================

ordered_matches AS (

    SELECT
        *,

        /*
            Convert match points into a compact result representation.

            W = win
            D = draw
            L = loss
        */
        CASE
            WHEN points = 3 THEN 'W'
            WHEN points = 1 THEN 'D'
            ELSE 'L'
        END AS result,

        /*
            The source dataset does not contain official matchday numbers.

            ROW_NUMBER therefore creates a chronological match number
            separately for every team and season.
        */
        ROW_NUMBER() OVER (
            PARTITION BY
                season,
                team
            ORDER BY
                date,
                time,
                opponent
        ) AS match_number

    FROM team_matches
),


-- ============================================================
-- 3. Calculate rolling form over the last five matches
-- ============================================================

rolling_form AS (

    SELECT
        *,

        /*
            Current row + four previous rows = maximum of five matches.

            PARTITION BY season, team prevents the rolling window
            from crossing team or season boundaries.
        */
        SUM(points) OVER (
            PARTITION BY
                season,
                team
            ORDER BY
                match_number
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS last_5_points,


        /*
            The first matches of a season do not yet have a full
            five-match window.

            Example:
                match 1 -> 1 observation
                match 2 -> 2 observations
                ...
                match 5 -> 5 observations
                match 6 -> still 5 observations
        */
        COUNT(*) OVER (
            PARTITION BY
                season,
                team
            ORDER BY
                match_number
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS matches_in_form_window,


        SUM(goals_for) OVER (
            PARTITION BY
                season,
                team
            ORDER BY
                match_number
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS last_5_goals_for,


        SUM(goals_against) OVER (
            PARTITION BY
                season,
                team
            ORDER BY
                match_number
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS last_5_goals_against,


        /*
            Build a readable representation of recent results.

            Example:
                WDWLL

            The correlated subquery selects the current match and up to
            four previous matches for the same team and season.

            STRING_AGG then concatenates individual match results
            in chronological order.
        */
        (
            SELECT STRING_AGG(
                previous_match.result,
                ''
                ORDER BY previous_match.match_number
            )

            FROM ordered_matches AS previous_match

            WHERE previous_match.season = ordered_matches.season
              AND previous_match.team = ordered_matches.team

              AND previous_match.match_number BETWEEN
                  ordered_matches.match_number - 4
                  AND ordered_matches.match_number

        ) AS last_5_form

    FROM ordered_matches
)


-- ============================================================
-- 4. Final result
-- ============================================================

SELECT
    season,
    team,
    match_number,

    date,
    opponent,
    venue,

    goals_for,
    goals_against,

    result,
    points,

    matches_in_form_window,

    last_5_form,

    last_5_points,

    /*
        Rolling points per match.

        We divide by the actual number of matches available in the
        rolling window instead of always dividing by five.
    */
    ROUND(
        last_5_points::NUMERIC
        / NULLIF(matches_in_form_window, 0),
        2
    ) AS last_5_points_per_match,

    last_5_goals_for,
    last_5_goals_against,

    last_5_goals_for
        - last_5_goals_against AS last_5_goal_difference

FROM rolling_form

ORDER BY
    season DESC,
    team,
    match_number;