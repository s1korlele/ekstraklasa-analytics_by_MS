/*
    File: 01_team_season_summary.sql
    Database: PostgreSQL 18
    Schema: public
    Source table: public.matches

    Purpose:
    Build season-level team statistics from match-level Ekstraklasa data.

    The source table stores one row per match with separate home and away
    columns. The first CTE transforms each fixture into two team-level rows,
    allowing further analysis to be performed from a consistent team
    perspective.

    The final result contains one row per team and season together with
    aggregated performance metrics and a statistical ranking.

    Note:
    statistical_rank is NOT intended to reproduce the official Ekstraklasa
    final standings in every tie scenario. Full head-to-head tie-breaking
    logic is implemented separately in the Python analytics layer.
*/


-- ============================================================
-- 1. Transform match-level data into team-level observations
-- ============================================================

WITH team_matches AS (

    -- Home team's perspective
    SELECT
        season,
        date,
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
        away_team AS team,
        home_team AS opponent,
        'away' AS venue,
        away_goals AS goals_for,
        home_goals AS goals_against,
        away_points AS points
    FROM public.matches
),


-- ============================================================
-- 2. Aggregate performance by team and season
-- ============================================================

team_season_summary AS (

    SELECT
        season,
        team,

        COUNT(*) AS matches,

        -- PostgreSQL FILTER syntax is used for conditional aggregation.
        COUNT(*) FILTER (
            WHERE points = 3
        ) AS wins,

        COUNT(*) FILTER (
            WHERE points = 1
        ) AS draws,

        COUNT(*) FILTER (
            WHERE points = 0
        ) AS losses,

        SUM(goals_for) AS goals_for,
        SUM(goals_against) AS goals_against,

        SUM(goals_for)
            - SUM(goals_against) AS goal_difference,

        SUM(points) AS points

    FROM team_matches

    GROUP BY
        season,
        team
),


-- ============================================================
-- 3. Create a statistical ranking within each season
-- ============================================================

season_ranking AS (

    SELECT
        *,

        /*
            ROW_NUMBER assigns a unique sequential position
            within each season.

            PARTITION BY restarts the ranking for every season.

            Statistical ranking criteria:
                1. points
                2. goal difference
                3. goals scored

            This does not reproduce all official Ekstraklasa
            head-to-head tie-breaking rules.
        */
        ROW_NUMBER() OVER (
            PARTITION BY season
            ORDER BY
                points DESC,
                goal_difference DESC,
                goals_for DESC
        ) AS statistical_rank

    FROM team_season_summary
)


-- ============================================================
-- 4. Final result
-- ============================================================

SELECT
    season,
    statistical_rank,
    team,
    matches,
    wins,
    draws,
    losses,
    goals_for,
    goals_against,
    goal_difference,
    points

FROM season_ranking

ORDER BY
    season DESC,
    statistical_rank;