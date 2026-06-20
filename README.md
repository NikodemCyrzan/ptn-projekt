# Analiza Stack Overflow Developer Survey 2024 (PyQt6)

Aplikacja desktopowa do eksploracji i wizualizacji danych z ankiety
Stack Overflow Developer Survey 2024. Zbudowana w PyQt6 w architekturze
**Model-View-Controller** z wykorzystaniem klasycznych wzorców projektowych.

## Uruchomienie

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt
python main.py                  # użyje domyślnego stack-overflow.csv
python main.py ścieżka/do/pliku.csv
```

## Testy

```bash
pytest -q
```

## Styl kodu (flake8)

```bash
pip install -r requirements-dev.txt
flake8 src main.py tests conftest.py
```

Konfiguracja w pliku `.flake8` (limit linii 100, `snake_case`/`PascalCase`,
docstringi). Kod przechodzi lint bez ostrzeżeń.

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

## Odpowiedzi na pytania obowiązkowe

**a) Dlaczego metody są dostosowane do danych?**

- Wynagrodzenia mają rozkład silnie prawoskośny (pojedyncze wartości
    > 1 mln USD) - **box plot** i **mediana** opisują je lepiej niż średnia,
    > a skrajne outliery są odcinane dla czytelności.
- Ranking 20+ języków wymaga **poziomego** bar chartu - długie nazwy
  pozostają czytelne.
- Satysfakcja (skala 0-10) wobec trybu pracy to porównanie kilku kategorii ->
  **grouped bar chart**.
- Heatmapa korelacji ma sens wyłącznie dla zmiennych **numerycznych** -
  dlatego stosujemy ją po konwersji typów.
- Pola wielokrotnego wyboru (języki) rozdzielone `;` są parsowane do list i
  "rozbijane" (`explode`) przed zliczaniem.

**b) Rozwiązania programistyczne:**

- **MVC** - modele nie importują Qt, widoki nie liczą, kontroler łączy je
  sygnałami/slotami.
- **Strategy** - nowa analiza = nowa klasa, bez zmian w widoku i kontrolerze.
- **Observer** - luźne powiązanie komponentów dzięki sygnałom Qt.
- **Singleton + Facade** - jednokrotne, ukryte za prostym API wczytanie i
  czyszczenie dużego zbioru danych.

## Obsługa wyjątków

- Brak pliku CSV -> `QMessageBox` + `QFileDialog` do wskazania innego pliku.
- Pusty wynik filtrowania -> komunikat w panelu wniosków.
- Błąd renderowania wykresu -> puste płótno + komunikat na pasku statusu.
- Brak wymaganej kolumny -> informacja zamiast wywrócenia aplikacji.
