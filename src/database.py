from pathlib import Path
import os

import pandas as pd
import psycopg
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


def get_connection():
    """Tworzy i zwraca połączenie z bazą PostgreSQL."""

    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5,
    )


def load_matches_from_db():
    """Pobiera dane meczowe z PostgreSQL jako DataFrame."""

    query = """
        SELECT
            season,
            date,
            time,
            home_team,
            away_team,
            home_goals,
            away_goals,
            result,
            home_points,
            away_points,
            total_goals,
            goal_difference
        FROM public.matches
        ORDER BY date, time;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)

            rows = cursor.fetchall()

            columns = [
                description.name
                for description in cursor.description
            ]

    df = pd.DataFrame(rows, columns=columns)

    df["date"] = pd.to_datetime(df["date"])

    return df