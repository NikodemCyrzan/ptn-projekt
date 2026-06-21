Nikodem Cyrzan s30161, Michał Kujawa s26408 

# Analiza Stack Overflow Developer Survey 2024 (PyQt6)

Aplikacja desktopowa do eksploracji i wizualizacji danych z ankiety
Stack Overflow Developer Survey 2024. Zbudowana w PyQt6 w architekturze
**Model-View-Controller** z wykorzystaniem klasycznych wzorców projektowych.

## Uruchomienie

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
python main.py ścieżka/do/pliku.csv
```

## Testy

```bash
pytest -q
```

## flake8

```bash
pip install -r requirements-dev.txt
flake8 src main.py tests conftest.py
```

## Funkcje

- **Wczytywanie i eksploracja** - sortowalna tabela (`QTableView` +
  `QSortFilterProxyModel`) z wyszukiwarką.
- **Filtrowanie** - panel boczny: kraj, język programowania, zakres lat
  doświadczenia (suwaki).
- **Analizy** (menu _Analiza_):
    1. Popularność języków programowania (poziomy bar chart),
    2. Wynagrodzenia wg krajów (mediana/kwartyle),
    3. Wynagrodzenie vs doświadczenie (box plot),
    4. Satysfakcja vs tryb pracy (bar chart),
    5. AI vs wynagrodzenie/satysfakcja,
    6. Korelacje zmiennych numerycznych (heatmapa).
- **Automatyczne wnioski** - panel pod wykresem generuje zdania opisowe.
- **Sterowanie** - mysz + skróty: `Ctrl+Q` (zamknij), `F5` (odśwież).

## Zastosowane wzorce projektowe

| Wzorzec       | Zastosowanie                                                         |
| ------------- | -------------------------------------------------------------------- |
| **Strategy**  | `Analyzer` (ABC) i podklasy - wymienne algorytmy analizy.            |
| **Observer**  | Sygnały/sloty Qt (`filters_changed`, `analysis_selected`).           |
| **Singleton** | `DataLoader` - dane wczytywane raz, współdzielone.                   |
| **Facade**    | `DataPipeline` - ukrywa potok load -> clean za jednym konstruktorem. |
