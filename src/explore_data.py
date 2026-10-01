from pathlib import Path
import pandas as pd


# Ścieżka do głównego katalogu projektu
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Ścieżka do surowych danych
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "POL.csv"


# Wczytanie danych
df = pd.read_csv(DATA_PATH)


print("=== EKSTRAKLASA DATASET ===")

print(f"\nLiczba meczów: {len(df)}")
print(f"Liczba kolumn: {len(df.columns)}")

print("\nKolumny:")
print(df.columns.tolist())

print("\nDostępne sezony:")
print(df["Season"].unique())

print("\nLiczba meczów w każdym sezonie:")
print(df["Season"].value_counts().sort_index())

print("\nBraki danych:")
print(df.isnull().sum())

print("\nPierwsze 5 rekordów:")
print(df.head())