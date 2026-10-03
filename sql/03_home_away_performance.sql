/*
    File: 03_home_away_performance.sql
    Database: PostgreSQL 18
    Schema: public
    Source table: public.matches

    Purpose:
    Compare home and away performance for each team and season.

    The source table contains one row per fixture. Each fixture is transformed
    into two team-level observations: one for the home team and one for the
    away team.

    The analysis compares points, goals and results between home and away
    matches. Points per match is used as the main comparable metric because
    teams may have played different numbers of home and away matches,
    especially during the current season.
*/


-- ============================================================
-- 1. Transform fixtures into team-level observations
-- ============================================================

WITH team_matches AS (

    SELECT
        season,
        date,
        home_team AS team,
        'home' AS venue,
        home_goals AS goals_for,
        away_goals AS goals_against,
        home_points AS points
    FROM public.matches

    UNION ALL

    SELECT
        season,
        date,
        away_team AS team,
        'away' AS venue,
        away_goals AS goals_for,
        home_goals AS goals_against,
        away_points AS points
    FROM public.matches
),


-- ============================================================
-- 2. Aggregate home and away statistics
-- ============================================================

home_away_summary AS (

    SELECT
        season,
        team,

        COUNT(*) FILTER (
            WHERE venue = 'home'
        ) AS home_matches,

        COUNT(*) FILTER (
            WHERE venue = 'away'
        ) AS away_matches,


        -- Results

        COUNT(*) FILTER (
            WHERE venue = 'home'
              AND points = 3
        ) AS home_wins,

        COUNT(*) FILTER (
            WHERE venue = 'away'
              AND points = 3
        ) AS away_wins,

        COUNT(*) FILTER (
            WHERE venue = 'home'
              AND points = 1
        ) AS home_draws,

        COUNT(*) FILTER (
            WHERE venue = 'away'
              AND points = 1
        ) AS away_draws,

        COUNT(*) FILTER (
            WHERE venue = 'home'
              AND points = 0
        ) AS home_losses,

        COUNT(*) FILTER (
            WHERE venue = 'away'
              AND points = 0
        ) AS away_losses,


        -- Points

        SUM(points) FILTER (
            WHERE venue = 'home'
        ) AS home_points,

        SUM(points) FILTER (
            WHERE venue = 'away'
        ) AS away_points,


        -- Goals scored

        SUM(goals_for) FILTER (
            WHERE venue = 'home'
        ) AS home_goals_for,

        SUM(goals_for) FILTER (
            WHERE venue = 'away'
        ) AS away_goals_for,


        -- Goals conceded

        SUM(goals_against) FILTER (
            WHERE venue = 'home'
        ) AS home_goals_against,

        SUM(goals_against) FILTER (
            WHERE venue = 'away'
        ) AS away_goals_against

    FROM team_matches

    GROUP BY
        season,
        team
),


-- ============================================================
-- 3. Calculate comparable performance metrics
-- ============================================================

home_away_metrics AS (

    SELECT
        *,

        ROUND(
            home_points::NUMERIC
            / NULLIF(home_matches, 0),
            2
        ) AS home_points_per_match,

        ROUND(
            away_points::NUMERIC
            / NULLIF(away_matches, 0),
            2
        ) AS away_points_per_match,

        ROUND(
            home_goals_for::NUMERIC
            / NULLIF(home_matches, 0),
            2
        ) AS home_goals_per_match,

        ROUND(
            away_goals_for::NUMERIC
            / NULLIF(away_matches, 0),
            2
        ) AS away_goals_per_match

    FROM home_away_summary
)


-- ============================================================
-- 4. Final result
-- ============================================================

SELECT
    season,
    team,

    home_matches,
    away_matches,

    home_wins,
    home_draws,
    home_losses,

    away_wins,
    away_draws,
    away_losses,

    home_points,
    away_points,

    home_points_per_match,
    away_points_per_match,

    ROUND(
        home_points_per_match
        - away_points_per_match,
        2
    ) AS home_advantage_ppm,

    home_goals_for,
    away_goals_for,

    home_goals_against,
    away_goals_against,

    home_goals_per_match,
    away_goals_per_match

FROM home_away_metrics

ORDER BY
    season DESC,
    home_advantage_ppm DESC;