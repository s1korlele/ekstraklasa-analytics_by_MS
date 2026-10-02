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

# 4. Ujednolicenie nazw drużyn
team_names = {
    "Arka Gdynia": "Arka Gdynia",
    "Cracovia": "Cracovia",
    "GKS Belchatow": "GKS Bełchatów",
    "GKS Katowice": "GKS Katowice",
    "Gornik Z.": "Górnik Zabrze",
    "Gornik Zabrze": "Górnik Zabrze",
    "Jagiellonia": "Jagiellonia Białystok",
    "Korona Kielce": "Korona Kielce",
    "LKS Lodz": "ŁKS Łódź",
    "Lech Poznan": "Lech Poznań",
    "Lechia Gdansk": "Lechia Gdańsk",
    "Leczna": "Górnik Łęczna",
    "Legia": "Legia Warszawa",
    "Legnica": "Miedź Legnica",
    "Motor Lublin": "Motor Lublin",
    "Piast Gliwice": "Piast Gliwice",
    "Podbeskidzie": "Podbeskidzie Bielsko-Biała",
    "Pogon Szczecin": "Pogoń Szczecin",
    "Polonia Warszawa": "Polonia Warszawa",
    "Puszcza": "Puszcza Niepołomice",
    "Radomiak Radom": "Radomiak Radom",
    "Rakow": "Raków Częstochowa",
    "Ruch": "Ruch Chorzów",
    "Ruch Chorzow": "Ruch Chorzów",
    "Sandecja Nowy S.": "Sandecja Nowy Sącz",
    "Slask Wroclaw": "Śląsk Wrocław",
    "Stal Mielec": "Stal Mielec",
    "Termalica B-B.": "Bruk-Bet Termalica Nieciecza",
    "Warta Poznan": "Warta Poznań",
    "Widzew Lodz": "Widzew Łódź",
    "Wieczysta Krakow": "Wieczysta Kraków",
    "Wisla": "Wisła Kraków",
    "Wisla Plock": "Wisła Płock",
    "Zaglebie": "Zagłębie Lubin",
    "Zaglebie Sosnowiec": "Zagłębie Sosnowiec",
    "Zawisza": "Zawisza Bydgoszcz",
}

df["home_team"] = df["home_team"].replace(team_names)
df["away_team"] = df["away_team"].replace(team_names)

# 5. Konwersja daty
df["date"] = pd.to_datetime(
    df["date"],
    format="%d/%m/%Y"
)

# 6. Punkty zdobyte przez gospodarzy i gości
df["home_points"] = df["result"].map({
    "H": 3,
    "D": 1,
    "A": 0
})

df["away_points"] = df["result"].map({
    "H": 0,
    "D": 1,
    "A": 3
})


# 7. Dodatkowe statystyki meczu
df["total_goals"] = df["home_goals"] + df["away_goals"]

df["goal_difference"] = (
    df["home_goals"] - df["away_goals"]
)

# 8. Zapis przetworzonych danych
df.to_csv(PROCESSED_DATA_PATH, index=False)


print("=== DATA PREPARATION COMPLETE ===")
print(f"Liczba meczów: {len(df)}")
print(f"Liczba kolumn: {len(df.columns)}")
print(f"Zapisano plik: {PROCESSED_DATA_PATH}")

print("\nPierwsze rekordy:")
print(df.head())