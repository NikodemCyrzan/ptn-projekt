# Plan projektu zaliczeniowego — analiza Stack Overflow Developer Survey (PyQt6)

## Temat i uzasadnienie wyboru danych

**Zbiór danych:** Stack Overflow Developer Survey 2024
**Źródło:** https://survey.stackoverflow.co/ (lub Kaggle)
**Format:** CSV, ~49 000 wierszy, ~80 kolumn

Zbiór jest idealny do tego zadania, ponieważ:

- zawiera mieszaninę danych **kategorycznych** (języki, narzędzia, kraje, typ pracy) i **numerycznych** (wynagrodzenia, lata doświadczenia),
- wymaga typowych operacji czyszczenia: konwersji typów, parsowania pól wielokrotnego wyboru (kolumny z odpowiedziami oddzielonymi `;`),
- pozwala formułować pytania analityczne zrozumiałe dla każdego (np. „co wpływa na zarobki programistów?").

---

## Pytania analityczne

1. Jakie języki programowania są najpopularniejsze i jak zmieniało się to w czasie?
2. Jak wykształcenie i lata doświadczenia wpływają na wynagrodzenie?
3. Które kraje mają najwyższe mediany wynagrodzeń i największe dysproporcje?
4. Jaki jest związek między trybem pracy (zdalny/hybrydowy/biurowy) a satysfakcją z pracy?
5. Czy programiści używający AI-assistants zarabiają lub są bardziej zadowoleni?

---

## Struktura projektu

```
stackoverflow_analysis/
├── data/
│   └── survey_results_public.csv
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── data_loader.py            # Model — wczytywanie i walidacja danych
│   │   ├── data_cleaner.py           # Model — czyszczenie, konwersje typów
│   │   └── analyzers.py              # Model — klasy analiz (Strategy)
│   ├── views/
│   │   ├── __init__.py
│   │   ├── main_window.py            # View — główne okno QMainWindow
│   │   ├── data_table_view.py        # View — tabela z danymi (QTableView)
│   │   ├── chart_widget.py           # View — wrapper na Matplotlib canvas
│   │   ├── filters_panel.py          # View — panel filtrów po lewej
│   │   └── conclusions_panel.py      # View — panel wniosków na dole
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── analysis_controller.py    # Controller — łączy model i widoki
│   └── utils/
│       ├── __init__.py
│       └── constants.py              # stałe: ścieżki, kolory, nazwy kolumn
├── tests/
│   ├── test_data_cleaner.py
│   ├── test_analyzers.py
│   └── test_data_loader.py
├── main.py                           # punkt wejścia (QApplication)
├── requirements.txt
└── README.md
```

---

## Architektura — wzorzec MVC

Program stosuje architekturę **Model–View–Controller**, naturalną dla PyQt6:

```
┌────────────────────────────────────────────────────────────────────┐
│                         AnalysisController                        │
│  • reaguje na sygnały z widoków (filtry, przyciski)               │
│  • wywołuje odpowiedni Analyzer                                  │
│  • aktualizuje ChartWidget i ConclusionsPanel                    │
└────────┬──────────────────────────────────────────────┬───────────┘
         │  manipuluje                                  │  aktualizuje
         ▼                                              ▼
┌─────────────────────┐                    ┌─────────────────────────┐
│       MODELS        │                    │         VIEWS           │
│ DataLoader          │                    │ MainWindow              │
│ DataCleaner         │                    │ ├─ FiltersPanel (lewy)  │
│ SalaryAnalyzer      │                    │ ├─ DataTableView (tab)  │
│ PopularityAnalyzer  │                    │ ├─ ChartWidget (tab)    │
│ SatisfactionAnalyzer│                    │ └─ ConclusionsPanel     │
└─────────────────────┘                    └─────────────────────────┘
```

**Przepływ danych:**

1. Użytkownik zmienia filtry w `FiltersPanel` → sygnał Qt `filters_changed`
2. `AnalysisController` odbiera sygnał → wywołuje odpowiedni `Analyzer.run(df)`
3. Controller przekazuje wynik do `ChartWidget.plot()` i `ConclusionsPanel.update()`

---

## Klasy — szczegóły

### Warstwa Model

| Klasa                  | Odpowiedzialność                                                         |
| ---------------------- | ------------------------------------------------------------------------ |
| `DataLoader`           | Singleton. Wczytanie CSV, walidacja, obsługa encoding/błędów pliku.      |
| `DataCleaner`          | Czyszczenie braków, konwersja typów, parsowanie pól wielokrotnych (`;`). |
| `Analyzer` (ABC)       | Interfejs bazowy — metody `run(df) -> DataFrame` i `describe() -> str`.  |
| `SalaryAnalyzer`       | Mediana/kwartyle wynagrodzeń wg krajów, doświadczenia, wykształcenia.    |
| `PopularityAnalyzer`   | Ranking technologii, zliczanie odpowiedzi, rozbijanie pól wielokrotnych. |
| `SatisfactionAnalyzer` | Analiza satysfakcji vs tryb pracy, użycie AI.                            |

### Warstwa View

| Klasa              | Widget Qt                                       | Opis                                                                                            |
| ------------------ | ----------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `MainWindow`       | `QMainWindow`                                   | Główne okno: menu bar, splitter, statusbar.                                                     |
| `FiltersPanel`     | `QWidget` z `QComboBox`, `QCheckBox`, `QSlider` | Panel boczny: filtr kraju, języka, zakresu lat doświadczenia. Emituje sygnał `filters_changed`. |
| `DataTableView`    | `QTableView` + `QSortFilterProxyModel`          | Tabela z danymi — sortowanie kliknięciem nagłówka, wyszukiwarka.                                |
| `ChartWidget`      | `FigureCanvasQTAgg` (matplotlib backend)        | Osadza wykres matplotlib wewnątrz Qt. Metoda `plot(fig)` podmienia canvas.                      |
| `ConclusionsPanel` | `QTextEdit` (readonly)                          | Wyświetla automatyczne wnioski tekstowe pod wykresem.                                           |

### Warstwa Controller

| Klasa                | Opis                                                                                                                         |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `AnalysisController` | Łączy sygnały widoków ze slotami wywołującymi analizatory. Przechowuje referencję do `DataPipeline` i aktualnego `Analyzer`. |

---

## Wzorce projektowe

### 1. Strategy — wymienne analizatory

Każdy analizator implementuje ten sam interfejs. `AnalysisController` przechowuje `current_analyzer` i podmienia go gdy użytkownik wybierze inną analizę w menu.

```python
from abc import ABC, abstractmethod
import pandas as pd

class Analyzer(ABC):
    """Bazowa klasa analizy (Strategy interface)."""

    @abstractmethod
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """Wykonaj analizę i zwróć wynik."""
        ...

    @abstractmethod
    def describe(self, result: pd.DataFrame) -> str:
        """Generuj wnioski tekstowe z wyniku."""
        ...

    @abstractmethod
    def chart_type(self) -> str:
        """Zwróć typ wykresu: 'bar', 'boxplot', 'heatmap', 'choropleth'."""
        ...

class SalaryAnalyzer(Analyzer):
    def run(self, df):
        return (
            df.dropna(subset=["ConvertedCompYearly"])
              .groupby("Country")["ConvertedCompYearly"]
              .agg(["median", "mean", "count"])
              .query("count >= 30")
              .sort_values("median", ascending=False)
              .head(20)
        )

    def describe(self, result):
        top = result.index[0]
        val = result.loc[top, "median"]
        return f"Najwyższa mediana wynagrodzeń: {top} ({val:,.0f} USD)."

    def chart_type(self):
        return "barh"
```

### 2. Observer — sygnały i sloty Qt

PyQt6 natywnie implementuje Observer. `FiltersPanel` emituje sygnał — `AnalysisController` reaguje bez bezpośredniej zależności widok→model.

```python
from PyQt6.QtCore import pyqtSignal

class FiltersPanel(QWidget):
    filters_changed = pyqtSignal(dict)  # {"country": "Poland", "min_exp": 3, ...}

    def _on_combo_changed(self):
        self.filters_changed.emit(self._collect_filters())

# W controllerze:
class AnalysisController:
    def __init__(self, filters_panel, chart_widget, conclusions_panel, pipeline):
        filters_panel.filters_changed.connect(self._on_filters_changed)

    def _on_filters_changed(self, filters: dict):
        filtered_df = self._apply_filters(self.pipeline.df, filters)
        result = self.current_analyzer.run(filtered_df)
        self.chart_widget.plot(result, self.current_analyzer.chart_type())
        self.conclusions_panel.set_text(self.current_analyzer.describe(result))
```

### 3. Singleton — jednokrotne wczytanie danych

```python
class DataLoader:
    _instance = None
    _df = None

    def __new__(cls, path: str = ""):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, path: str) -> pd.DataFrame:
        if self._df is None:
            self._df = pd.read_csv(path, low_memory=False)
        return self._df
```

### 4. Facade — DataPipeline

```python
class DataPipeline:
    """Facade: load → clean w jednym wywołaniu."""

    def __init__(self, path: str):
        raw = DataLoader().load(path)
        self.df = DataCleaner(raw).clean()
```

---

## Layout głównego okna

```
┌──────────────────────────────────────────────────────────────────┐
│  Menu: [Plik ▾]  [Analiza ▾]  [Pomoc ▾]                        │
├──────────┬───────────────────────────────────────────────────────┤
│ FILTRY   │  ┌─────────┐ ┌─────────┐                            │
│          │  │ Tabela   │ │ Wykres  │   ← QTabWidget (2 taby)    │
│ Kraj:    │  └─────────┘ └─────────┘                            │
│ [▾ All ] │                                                      │
│          │  ┌──────────────────────────────────────────────────┐│
│ Język:   │  │                                                  ││
│ [▾ All ] │  │            ChartWidget / DataTableView           ││
│          │  │            (aktywny tab)                          ││
│ Doświad- │  │                                                  ││
│ czenie:  │  │                                                  ││
│ [===●==] │  └──────────────────────────────────────────────────┘│
│ 0-30 lat │                                                      │
│          │  ┌──────────────────────────────────────────────────┐│
│ [Filtruj]│  │  ConclusionsPanel                                ││
│ [Reset]  │  │  „Mediana wynagrodzeń w Polsce: 42 000 USD..."   ││
│          │  └──────────────────────────────────────────────────┘│
├──────────┴───────────────────────────────────────────────────────┤
│  Status: Wczytano 48 726 rekordów │ Filtr aktywny: Polska      │
└──────────────────────────────────────────────────────────────────┘
```

- **Splitter** (`QSplitter`) dzieli okno na panel filtrów (stała szer. ~220px) i główny obszar.
- **QTabWidget** przełącza między widokiem tabeli a wykresem.
- **QStatusBar** pokazuje liczbę rekordów i aktywne filtry.

---

## Wizualizacje — typy wykresów i uzasadnienie

| Analiza                         | Typ wykresu       | Widget                                 | Uzasadnienie                                                      |
| ------------------------------- | ----------------- | -------------------------------------- | ----------------------------------------------------------------- |
| Popularność języków             | Poziomy bar chart | `ChartWidget` (matplotlib `barh`)      | Porównanie wielu kategorii; poziomy układ → długie nazwy czytelne |
| Wynagrodzenie vs. doświadczenie | Box plot          | `ChartWidget` (seaborn `boxplot`)      | Rozkład skośny z outliersami; mediana ważniejsza od średniej      |
| Wynagrodzenia wg krajów         | Choropleth        | `ChartWidget` (matplotlib + geopandas) | Dane geograficzne naturalnie mapują się na mapę                   |
| Satysfakcja vs. tryb pracy      | Grouped bar chart | `ChartWidget` (seaborn `countplot`)    | Porównanie kilku kategorii w dwóch wymiarach                      |
| Korelacje numeryczne            | Heatmapa          | `ChartWidget` (seaborn `heatmap`)      | Macierz korelacji — standard dla wizualizacji zależności          |

Każdy `Analyzer` deklaruje swój `chart_type()` — `Visualizer` dobiera metodę rysowania automatycznie.

---

## Wymagania funkcjonalne — mapowanie

| Wymaganie                      | Realizacja w PyQt6                                                         |
| ------------------------------ | -------------------------------------------------------------------------- |
| **A1** wczytanie i eksploracja | `DataLoader` + `DataTableView` z sortowaniem i wyszukiwaniem               |
| **A2** manipulacje, konwersje  | `DataCleaner`: explode pól `;`, konwersja `$` → float, mapowanie kategorii |
| **A3** sortowanie, filtrowanie | `QSortFilterProxyModel` w tabeli + `FiltersPanel` z combo/sliderem         |
| **A4** wizualizacja            | `ChartWidget` z osadzonym matplotlib — 5 typów wykresów                    |
| **A5** wnioski                 | `ConclusionsPanel` — auto-generowane zdania z `Analyzer.describe()`        |
| **A6** sterowanie              | Mysz + klawiatura; `QShortcut` dla Ctrl+Q (zamknij), F5 (odśwież)          |

---

## Wymagania programistyczne — mapowanie

| Wymaganie     | Realizacja                                                                                      |
| ------------- | ----------------------------------------------------------------------------------------------- |
| **B1** OOP    | Osobne klasy per odpowiedzialność; dziedziczenie `Analyzer(ABC)`                                |
| **B2** wzorce | Strategy (analizatory), Observer (sygnały/sloty), Singleton (DataLoader), Facade (DataPipeline) |
| **B3** styl   | `snake_case`, `PascalCase`, docstringi Google-style, `flake8`                                   |
| **B4** testy  | `pytest`: test_data_cleaner, test_analyzers, test_data_loader                                   |

---

## Obsługa wyjątków

| Sytuacja                  | Obsługa                                                              |
| ------------------------- | -------------------------------------------------------------------- |
| Brak pliku CSV            | `QMessageBox.critical()` + `QFileDialog` do wskazania innego pliku   |
| Zły encoding / separator  | `try/except pd.errors.ParserError` → dialog z informacją             |
| Brak wymaganej kolumny    | `KeyError` → `QMessageBox.warning()` + powrót do domyślnej analizy   |
| Pusty wynik filtrowania   | Komunikat w `ConclusionsPanel`: „Brak danych spełniających kryteria" |
| Błąd renderowania wykresu | `try/except` w `ChartWidget.plot()` → pusty canvas + log w statusbar |

---

## Testy jednostkowe (pytest)

```python
def test_parse_multi_choice():
    """Kolumna 'Python;JavaScript' → lista ['Python', 'JavaScript']."""
    row = pd.DataFrame({"LanguageHaveWorkedWith": ["Python;JavaScript"]})
    result = DataCleaner(row).parse_multi_choice("LanguageHaveWorkedWith")
    assert result.iloc[0] == ["Python", "JavaScript"]

def test_salary_conversion():
    """String '85000' → float 85000.0, a 'NA' → NaN."""
    row = pd.DataFrame({"ConvertedCompYearly": ["85000", "NA"]})
    result = DataCleaner(row).convert_salary()
    assert result["ConvertedCompYearly"].iloc[0] == 85000.0
    assert pd.isna(result["ConvertedCompYearly"].iloc[1])

def test_salary_analyzer_top_country():
    """Wynik ma kolumny median, mean, count i jest posortowany malejąco."""
    df = pd.DataFrame({
        "Country": ["PL"]*50 + ["US"]*50,
        "ConvertedCompYearly": [40000]*50 + [100000]*50
    })
    result = SalaryAnalyzer().run(df)
    assert result.index[0] == "US"
    assert result.loc["US", "median"] == 100000

def test_analyzer_empty_df():
    """Pusty DataFrame nie rzuca wyjątku — zwraca pusty wynik."""
    result = SalaryAnalyzer().run(pd.DataFrame())
    assert len(result) == 0

# test_data_loader.py
def test_missing_file():
    """Brak pliku = FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        DataLoader().load("nonexistent.csv")
```

---

## requirements.txt

```
numpy>=1.26
pandas>=2.1
matplotlib>=3.8
seaborn>=0.13
PyQt6>=6.6
geopandas>=0.14
pytest>=7.4
```

---

## README — szkic odpowiedzi na obowiązkowe pytania

**a) Dlaczego metody są dostosowane do danych?**

- Dane o wynagrodzeniach mają rozkład silnie prawoskośny (kilka zarobków >500k USD) — box ploty pokazują medianę i outliersy lepiej niż bar chart ze średnią.
- Ranking 20+ języków programowania wymaga poziomego bar chartu — pionowy byłby nieczytelny.
- Dane geograficzne (kraj → wartość) naturalnie mapują się na choropleth.
- Heatmapa korelacji ma sens wyłącznie dla zmiennych numerycznych — dlatego stosujemy ją dopiero po konwersji zmiennych porządkowych na numeryczne.
- Panel filtrów z combo boxami odpowiada danym kategorycznym, a slider — danym numerycznym (lata doświadczenia).

**b) Rozwiązania programistyczne:**

- **MVC** — naturalny podział dla PyQt6: modele (logika) nie importują Qt, widoki nie robią obliczeń, controller łączy je sygnałami/slotami.
- **Strategy** — nowy analizator = nowa klasa bez zmiany controllera ani widoku.
- **Observer** — sygnały Qt (`filters_changed`, `analysis_selected`) zapewniają luźne powiązanie komponentów.
- **Singleton** — dane wczytywane raz przy starcie; wielu analizatorów współdzieli ten sam DataFrame.
- **Facade** — `DataPipeline` ukrywa load→clean za jednym konstruktorem.

---

## Harmonogram implementacji

| Etap | Zadanie                                            | Czas |
| ---- | -------------------------------------------------- | ---- |
| 1    | Pobranie danych, eksploracja w Jupyter             | 1h   |
| 2    | `DataLoader` + `DataCleaner` + testy               | 2h   |
| 3    | Trzy klasy `Analyzer` + testy                      | 2h   |
| 4    | `MainWindow` + `FiltersPanel` (layout, sygnały)    | 2h   |
| 5    | `ChartWidget` + osadzenie matplotlib w Qt          | 2h   |
| 6    | `DataTableView` + `QSortFilterProxyModel`          | 1h   |
| 7    | `AnalysisController` — połączenie warstw           | 1h   |
| 8    | `ConclusionsPanel` + statusbar + skróty klawiszowe | 1h   |
| 9    | README, requirements.txt, finalne testy, packaging | 1h   |
