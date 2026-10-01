from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "POL.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "matches.csv"


# 1. Wczytanie surowych danych
df = pd.read_csv(RAW_DATA_PATH)


# 2. Wybór kolumn potrzebnych do analizy
columns = [
    "Season",
    "Date",
    "Time",
    "Home",
    "Away",
    "HG",
    "AG",
    "Res",
]

df = df[columns].copy()


# 3. Czytelniejsze nazwy kolumn
df = df.rename(columns={
    "Season": "season",
    "Date": "date",
    "Time": "time",
    "Home": "home_team",
    "Away": "away_team",
    "HG": "home_goals",
    "AG": "away_goals",
    "Res": "result",
})


# 4. Konwersja daty
df["date"] = pd.to_datetime(
    df["date"],
    format="%d/%m/%Y"
)


# 5. Zapis przetworzonych danych
df.to_csv(PROCESSED_DATA_PATH, index=False)


print("=== DATA PREPARATION COMPLETE ===")
print(f"Liczba meczów: {len(df)}")
print(f"Liczba kolumn: {len(df.columns)}")
print(f"Zapisano plik: {PROCESSED_DATA_PATH}")

print("\nPierwsze rekordy:")
print(df.head())