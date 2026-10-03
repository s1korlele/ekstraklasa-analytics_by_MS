/*
    File: 02_season_over_season.sql
    Database: PostgreSQL 18
    Schema: public
    Source table: public.matches

    Purpose:
    Compare each team's performance with its previous Ekstraklasa season.

    Important:
    "Previous season" means the team's previous appearance in the dataset.

    If a club was relegated and returned several years later, LAG() compares
    the return season with the club's last Ekstraklasa season. Such cases are
    explicitly marked as 'return_after_gap'.

    The latest season available in the dataset is marked as 'current_season'.
    This avoids incorrectly treating historical seasons with different league
    formats as incomplete seasons.

    Raw point differences should be interpreted carefully for the current
    season. Points per match provides a more comparable performance metric.
*/


-- ============================================================
-- 1. Transform fixtures into team-level observations
-- ============================================================

WITH team_matches AS (

    SELECT
        season,
        home_team AS team,
        home_goals AS goals_for,
        away_goals AS goals_against,
        home_points AS points
    FROM public.matches

    UNION ALL

    SELECT
        season,
        away_team AS team,
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

        SUM(points) AS points,

        SUM(goals_for) AS goals_for,

        SUM(goals_against) AS goals_against,

        SUM(goals_for)
            - SUM(goals_against) AS goal_difference,

        ROUND(
            SUM(points)::NUMERIC
            / NULLIF(COUNT(*), 0),
            2
        ) AS points_per_match,

        /*
            Convert 2024/2025 -> 2024.

            Using a numeric season start year makes chronological
            comparisons explicit instead of relying on text sorting.
        */
        SPLIT_PART(
            season,
            '/',
            1
        )::INTEGER AS season_start_year

    FROM team_matches

    GROUP BY
        season,
        team
),


-- ============================================================
-- 3. Identify the latest season available in the dataset
-- ============================================================

dataset_info AS (

    SELECT
        MAX(season_start_year) AS latest_season_start_year

    FROM team_season_summary
),


-- ============================================================
-- 4. Retrieve the team's previous Ekstraklasa season
-- ============================================================

previous_season_data AS (

    SELECT
        *,

        LAG(season) OVER (
            PARTITION BY team
            ORDER BY season_start_year
        ) AS previous_season,

        LAG(season_start_year) OVER (
            PARTITION BY team
            ORDER BY season_start_year
        ) AS previous_season_start_year,

        LAG(matches) OVER (
            PARTITION BY team
            ORDER BY season_start_year
        ) AS previous_matches,

        LAG(points) OVER (
            PARTITION BY team
            ORDER BY season_start_year
        ) AS previous_points,

        LAG(points_per_match) OVER (
            PARTITION BY team
            ORDER BY season_start_year
        ) AS previous_points_per_match,

        LAG(goal_difference) OVER (
            PARTITION BY team
            ORDER BY season_start_year
        ) AS previous_goal_difference

    FROM team_season_summary
),


-- ============================================================
-- 5. Classify the type of season comparison
-- ============================================================

season_comparison AS (

    SELECT
        psd.*,

        CASE

            /*
                The latest season in the dataset is treated separately
                because it may still be in progress.
            */
            WHEN psd.season_start_year
                 = di.latest_season_start_year
                THEN 'current_season'

            /*
                A gap greater than one means that the club did not play
                in Ekstraklasa in at least one season between appearances.
            */
            WHEN psd.season_start_year
                 - psd.previous_season_start_year > 1
                THEN 'return_after_gap'

            ELSE 'consecutive'

        END AS comparison_type

    FROM previous_season_data AS psd

    CROSS JOIN dataset_info AS di
)


-- ============================================================
-- 6. Final result
-- ============================================================

SELECT
    team,
    season,
    previous_season,
    comparison_type,

    matches,
    previous_matches,

    points,
    previous_points,

    /*
        For current_season this value compares a partial total
        with the previous season's total and therefore should not
        be interpreted as a like-for-like performance metric.
    */
    points - previous_points AS points_change,

    points_per_match,
    previous_points_per_match,

    /*
        PPM is more suitable for comparisons when the number
        of played matches differs between seasons.
    */
    ROUND(
        points_per_match
        - previous_points_per_match,
        2
    ) AS points_per_match_change,

    goal_difference,
    previous_goal_difference,

    goal_difference
        - previous_goal_difference AS goal_difference_change

FROM season_comparison

/*
    A team's first appearance has no previous season to compare against,
    so it is excluded from the final comparison dataset.
*/
WHERE previous_season IS NOT NULL

ORDER BY
    team,
    season_start_year;