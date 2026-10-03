# ⚽ Ekstraklasa Analytics

Interaktywny projekt analityczny dotyczący polskiej Ekstraklasy, łączący przygotowanie i analizę danych w Pythonie, PostgreSQL i SQL oraz dashboard zbudowany w Streamlit i Plotly.

Projekt pokazuje pełny przepływ pracy z danymi:

**surowe dane → przygotowanie danych → PostgreSQL / SQL → Python / Pandas → dashboard Streamlit**

## 🌐 Live demo

**Dashboard:**  
https://ekstraklasa-analytics-ms.streamlit.app

---

## 🎯 Cel projektu

Celem projektu było stworzenie kompletnego rozwiązania analitycznego na rzeczywistych danych sportowych, obejmującego:

- eksplorację i kontrolę jakości danych,
- przygotowanie i transformację danych w Pythonie,
- analizę danych przy użyciu Pandas,
- pracę z PostgreSQL,
- tworzenie analiz SQL,
- wykorzystanie CTE, funkcji okienkowych i agregacji warunkowych,
- integrację Python ↔ PostgreSQL,
- implementację logiki tabeli ligowej,
- budowę interaktywnego dashboardu,
- wizualizację danych w Plotly,
- wersjonowanie projektu przy użyciu Git i GitHub,
- publiczny deployment aplikacji.

---

## 📊 Dashboard

Dashboard umożliwia analizę wyników Ekstraklasy według sezonu oraz wybranej drużyny.

### Widok ligi

Dla wybranego sezonu prezentowane są:

- liczba rozegranych meczów,
- liczba zdobytych bramek,
- średnia liczba goli na mecz,
- pełna tabela ligowa.

### Widok drużyny

Po wybraniu klubu dashboard prezentuje:

- liczbę rozegranych meczów,
- liczbę zdobytych punktów,
- bilans zwycięstw / remisów / porażek,
- bramki zdobyte i stracone,
- bilans bramek,
- średnią liczbę zdobytych bramek na mecz,
- tabelę ligową z wyróżnieniem wybranego klubu,
- pięć ostatnich spotkań i aktualną formę,
- historię pozycji drużyny w tabeli w trakcie sezonu.

Interaktywny wykres pozycji pozwala dodatkowo sprawdzić m.in. datę meczu, przeciwnika, wynik, miejsce rozegrania spotkania i liczbę zdobytych punktów.

---

## 🛠 Technologie

- **Python**
- **Pandas**
- **PostgreSQL**
- **SQL**
- **psycopg**
- **Streamlit**
- **Plotly**
- **Git / GitHub**
- **Streamlit Community Cloud**

---

## 🏗 Architektura projektu

```text
              Football-Data.co.uk
                      │
                      ▼
                   POL.csv
                      │
            ┌─────────┴─────────┐
            ▼                   ▼
    explore_data.py      prepare_data.py
                                │
                                ▼
                           matches.csv
                            │        │
                            │        └──────────────┐
                            ▼                       │
                       PostgreSQL                   │
                        │       │                   │
                        ▼       ▼                   │
                 SQL analytics  psycopg             │
                                │                   │
                                ▼                   │
                              Python ◄──── CSV fallback
                                │
                                ▼
                              Pandas
                                │
                                ▼
                        Plotly / Streamlit
```

W środowisku z dostępną bazą aplikacja pobiera dane z PostgreSQL poprzez `psycopg`.

Jeżeli połączenie z bazą nie jest dostępne, aplikacja automatycznie wykorzystuje przygotowany plik `matches.csv`. Publiczna wersja wdrożona w Streamlit Community Cloud działa w oparciu o ten mechanizm fallback.

Dzięki temu warstwa prezentacji może korzystać z tego samego formatu danych niezależnie od źródła.

---

## 🐍 Przygotowanie danych

Proces przygotowania danych znajduje się w:

```text
src/prepare_data.py
```

Obejmuje on:

1. wczytanie danych źródłowych,
2. wybór kolumn potrzebnych do analizy,
3. zmianę nazw kolumn,
4. ujednolicenie nazw klubów,
5. konwersję dat,
6. obliczenie punktów gospodarzy i gości,
7. utworzenie dodatkowych statystyk meczowych,
8. zapis przygotowanego zbioru do `data/processed/matches.csv`.

Przykładowe kolumny końcowego zbioru:

```text
season
date
time
home_team
away_team
home_goals
away_goals
result
home_points
away_points
total_goals
goal_difference
```

Nazwy klubów zostały znormalizowane, aby ten sam zespół nie występował w analizie pod różnymi wariantami nazwy.

Przed transformacją danych wykonywana jest również podstawowa eksploracja datasetu w `src/explore_data.py`, obejmująca m.in. kontrolę liczby rekordów, dostępnych sezonów, brakujących wartości i struktury danych.

---

## 🗄 PostgreSQL

Przygotowane dane zostały zaimportowane do tabeli `public.matches` w PostgreSQL.

Warstwa `src/database.py` odpowiada za:

- utworzenie połączenia z bazą,
- wykonanie zapytania pobierającego dane meczowe,
- utworzenie DataFrame,
- ujednolicenie typu kolumny z datą.

Dane dostępowe do bazy są pobierane ze zmiennych środowiskowych i nie są przechowywane bezpośrednio w kodzie ani repozytorium.

Aplikacja posiada również obsługę niedostępności PostgreSQL — w takim przypadku źródło danych jest automatycznie przełączane na przygotowany plik CSV.

---

## 🧮 Analizy SQL

Katalog `sql/` zawiera pięć analiz przygotowanych w PostgreSQL.

### `01_team_season_summary.sql`

Podsumowanie wyników drużyn w poszczególnych sezonach.

Obliczane są m.in.:

- mecze,
- zwycięstwa,
- remisy,
- porażki,
- gole zdobyte i stracone,
- bilans bramek,
- punkty.

Wykorzystane elementy SQL obejmują m.in. `CTE`, `UNION ALL`, `FILTER` oraz `ROW_NUMBER()`.

Ranking tworzony w tym zapytaniu ma charakter analityczny. Pełniejsza logika kolejności drużyn, obejmująca bezpośrednie spotkania, została zaimplementowana w Pythonie.

### `02_season_over_season.sql`

Analiza zmian wyników drużyn pomiędzy sezonami.

Wykorzystuje m.in.:

- `LAG()`,
- `PARTITION BY`,
- CTE,
- punkty na mecz,
- dynamiczne określenie najnowszego sezonu.

Analiza pozwala również odróżnić kolejny sezon klubu od powrotu do Ekstraklasy po przerwie.

### `03_home_away_performance.sql`

Porównanie wyników drużyn na własnym stadionie i na wyjeździe.

Analiza obejmuje m.in.:

- mecze,
- zwycięstwa / remisy / porażki,
- punkty,
- gole,
- punkty na mecz,
- gole na mecz,
- różnicę pomiędzy wynikami domowymi i wyjazdowymi.

### `04_team_form.sql`

Analiza bieżącej formy drużyn przy użyciu ruchomego okna ostatnich pięciu spotkań.

Wykorzystuje m.in.:

- `ROW_NUMBER()`,
- funkcje okienkowe,
- `ROWS BETWEEN 4 PRECEDING AND CURRENT ROW`,
- `STRING_AGG`.

Dla kolejnych spotkań obliczane są m.in. punkty, gole oraz sekwencja wyników.

### `05_advanced_analysis.sql`

Rozszerzenie analizy formy o porównanie kolejnych pięciomeczowych okien.

Przykład:

```text
mecze 1–5 → mecze 2–6
mecze 2–6 → mecze 3–7
mecze 3–7 → mecze 4–8
```

Na podstawie zmiany liczby punktów na mecz trend klasyfikowany jest jako:

```text
improving
declining
stable
insufficient_history
```

Porównanie wykonywane jest dopiero wtedy, gdy zarówno bieżące, jak i poprzednie okno zawierają komplet pięciu spotkań.

---

## 🏆 Logika tabeli ligowej

Tabela ligowa jest obliczana w Pythonie na podstawie danych meczowych.

Dla każdej drużyny wyliczane są:

- mecze,
- zwycięstwa,
- remisy,
- porażki,
- gole zdobyte,
- gole stracone,
- bilans bramek,
- punkty,
- zwycięstwa wyjazdowe.

Szczególna logika została zastosowana w przypadku drużyn posiadających taką samą liczbę punktów.

### Bezpośrednie spotkania — H2H

Dla grupy drużyn z równą liczbą punktów aplikacja sprawdza, czy zainteresowane zespoły rozegrały między sobą komplet bezpośrednich spotkań.

Jeżeli komplet spotkań został rozegrany, tworzona jest mini-tabela H2H i przy ustalaniu kolejności uwzględniane są m.in.:

- punkty zdobyte w bezpośrednich spotkaniach,
- bilans bramek H2H,
- w przypadku większej grupy również gole zdobyte H2H,
- następnie kryteria ogólne.

Jeżeli komplet bezpośrednich spotkań nie został jeszcze rozegrany, H2H jest pomijane, a kolejność ustalana jest według:

1. ogólnego bilansu bramek,
2. liczby zdobytych bramek,
3. liczby zwycięstw,
4. liczby zwycięstw na wyjeździe.

Dzięki temu mechanizm H2H może zostać zastosowany również w trakcie sezonu, jeżeli zainteresowane drużyny rozegrały już komplet spotkań między sobą.

---

## 📈 Historia pozycji drużyny

Dashboard umożliwia prześledzenie pozycji wybranego klubu w trakcie sezonu.

Dla każdego kolejnego meczu drużyny:

1. wybierane są wszystkie mecze ligowe rozegrane do tego dnia włącznie,
2. ponownie obliczana jest tabela ligowa,
3. odczytywana jest pozycja wybranego klubu,
4. zapisywane są informacje dotyczące danego spotkania.

### Metodologia

Źródłowy dataset nie zawiera oficjalnych numerów kolejek.

Ze względu na możliwość przekładania spotkań rekonstrukcja numerów kolejek wyłącznie na podstawie dat mogłaby prowadzić do nieprawidłowych wyników.

Z tego powodu projekt nie próbuje sztucznie odtwarzać oficjalnych kolejek.

**Oś X wykresu oznacza kolejny chronologicznie rozegrany mecz wybranej drużyny.**

Każdy punkt przedstawia pozycję zespołu w tabeli **na koniec dnia**, w którym rozegrany został dany mecz.

---

## 📁 Struktura projektu

```text
ekstraklasa-analytics_by_MS/
│
├── app/
│   └── app.py
│
├── data/
│   ├── processed/
│   │   └── matches.csv
│   └── raw/
│       └── POL.csv
│
├── sql/
│   ├── 01_team_season_summary.sql
│   ├── 02_season_over_season.sql
│   ├── 03_home_away_performance.sql
│   ├── 04_team_form.sql
│   └── 05_advanced_analysis.sql
│
├── src/
│   ├── database.py
│   ├── explore_data.py
│   ├── league_table.py
│   └── prepare_data.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

Surowy plik `POL.csv` nie jest przechowywany w repozytorium. Publiczna aplikacja korzysta z przygotowanego zbioru `data/processed/matches.csv`.

---

## ▶️ Uruchomienie projektu

Po sklonowaniu repozytorium należy utworzyć środowisko wirtualne i zainstalować zależności:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Następnie dashboard można uruchomić poleceniem:

```powershell
streamlit run app/app.py
```

Jeżeli połączenie z PostgreSQL nie jest dostępne, aplikacja automatycznie wykorzysta przygotowany plik CSV.

---

## 📚 Źródło danych

Dane meczowe wykorzystane w projekcie pochodzą z:

**Football-Data.co.uk**  
https://www.football-data.co.uk/

Źródłowy dataset zawiera m.in. informacje o sezonie, dacie meczu, drużynie gospodarzy i gości, wyniku oraz zdobytych bramkach.

Do projektu wybrano dane potrzebne do analizy wyników sportowych.

---

## ⚠️ Ograniczenia

Projekt posiada kilka świadomie przyjętych ograniczeń:

- źródłowe dane nie zawierają oficjalnych numerów kolejek,
- historia pozycji wykorzystuje kolejny rozegrany mecz drużyny zamiast rekonstruowanej kolejki,
- historyczna pozycja na wykresie przedstawia stan tabeli na koniec danego dnia,
- publiczna wersja aplikacji korzysta z przygotowanego CSV zamiast lokalnej instancji PostgreSQL,
- historyczne sezony Ekstraklasy korzystały z różnych formatów i zasad ustalania kolejności,
- dane źródłowe nie zawierają wszystkich potencjalnych informacji wymaganych do odwzorowania każdego historycznego kryterium regulaminowego.

Zamiast wprowadzać nieweryfikowalne założenia, ograniczenia wynikające ze źródła danych zostały pozostawione jawnie.

---

## 👤 Autor

**Marcin Sikora**

Projekt portfolio z obszaru Data / BI Analytics.

**GitHub:**  
https://github.com/s1korlele

**Live dashboard:**  
https://ekstraklasa-analytics-ms.streamlit.app