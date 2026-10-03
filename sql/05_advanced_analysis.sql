/*
    File: 05_advanced_analysis.sql
    Database: PostgreSQL 18
    Schema: public
    Source table: public.matches

    Purpose:
    Analyse changes in each team's recent form during an Ekstraklasa season.

    Team form is measured using a rolling five-match window.

    Example:
        after match 5 -> matches 1-5
        after match 6 -> matches 2-6
        after match 7 -> matches 3-7

    Each complete five-match window is compared with the immediately
    preceding five-match window. This allows us to identify whether
    recent team form is improving, declining or remaining stable.

    Important:
    The source dataset does not contain official matchday numbers.
    match_number therefore represents the chronological number of a match
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
        away_points AS points
    FROM public.matches
),


-- ============================================================
-- 2. Number matches chronologically for every team and season
-- ============================================================

ordered_matches AS (

    SELECT
        *,

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
-- 3. Calculate rolling five-match performance
-- ============================================================

rolling_form AS (

    SELECT
        *,

        /*
            Current match + four previous matches.

            Example:
                match 5 -> matches 1-5
                match 6 -> matches 2-6
                match 7 -> matches 3-7
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
            Used to distinguish a complete five-match window
            from the beginning of a season, where fewer than
            five matches are available.
        */
        COUNT(*) OVER (
            PARTITION BY
                season,
                team
            ORDER BY
                match_number
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS matches_in_window

    FROM ordered_matches
),


-- ============================================================
-- 4. Calculate points per match for each rolling window
-- ============================================================

rolling_metrics AS (

    SELECT
        *,

        ROUND(
            last_5_points::NUMERIC
            / NULLIF(matches_in_window, 0),
            2
        ) AS last_5_points_per_match

    FROM rolling_form
),


-- ============================================================
-- 5. Retrieve the previous rolling form measurement
-- ============================================================

form_comparison AS (

    SELECT
        *,

        /*
            LAG(..., 1) retrieves the rolling PPM calculated
            after the team's immediately preceding match.

            Example for match 6:

                current window  -> matches 2-6
                previous window -> matches 1-5

            The windows intentionally overlap because the purpose
            is to measure how recent five-match form changes
            after each newly played match.
        */
        LAG(
            last_5_points_per_match
        ) OVER (
            PARTITION BY
                season,
                team
            ORDER BY
                match_number
        ) AS previous_5_points_per_match,

        /*
            We also retrieve the size of the previous window.

            A form comparison is valid only when both the current
            and previous windows contain exactly five matches.
        */
        LAG(
            matches_in_window
        ) OVER (
            PARTITION BY
                season,
                team
            ORDER BY
                match_number
        ) AS previous_matches_in_window

    FROM rolling_metrics
)


-- ============================================================
-- 6. Final result
-- ============================================================

SELECT
    season,
    team,
    match_number,
    date,
    opponent,

    points,

    last_5_points,
    last_5_points_per_match,

    /*
        Previous rolling PPM is displayed only when both
        rolling windows contain five matches.
    */
    CASE
        WHEN matches_in_window = 5
         AND previous_matches_in_window = 5
            THEN previous_5_points_per_match
        ELSE NULL
    END AS previous_5_points_per_match,

    /*
        Difference between the current five-match form
        and the immediately preceding five-match form.
    */
    CASE
        WHEN matches_in_window = 5
         AND previous_matches_in_window = 5
            THEN ROUND(
                last_5_points_per_match
                - previous_5_points_per_match,
                2
            )
        ELSE NULL
    END AS form_change,

    CASE
        WHEN matches_in_window < 5
          OR previous_matches_in_window < 5
          OR previous_matches_in_window IS NULL
            THEN 'insufficient_history'

        WHEN last_5_points_per_match
             > previous_5_points_per_match
            THEN 'improving'

        WHEN last_5_points_per_match
             < previous_5_points_per_match
            THEN 'declining'

        ELSE 'stable'

    END AS form_trend

FROM form_comparison

ORDER BY
    season DESC,
    team,
    match_number;