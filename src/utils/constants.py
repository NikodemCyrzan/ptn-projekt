from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_DATA_DIR_CSV = PROJECT_ROOT / "data" / "survey_results_public.csv"
_ROOT_CSV = PROJECT_ROOT / "stack-overflow.csv"
DEFAULT_DATA_PATH = str(_DATA_DIR_CSV if _DATA_DIR_CSV.exists() else _ROOT_CSV)

COL_COUNTRY = "Country"
COL_SALARY = "ConvertedCompYearly"
COL_JOB_SAT = "JobSat"
COL_REMOTE = "RemoteWork"
COL_ED_LEVEL = "EdLevel"
COL_YEARS_PRO = "YearsCodePro"
COL_YEARS_CODE = "YearsCode"
COL_AGE = "Age"
COL_AI_SELECT = "AISelect"
COL_LANGUAGES = "LanguageHaveWorkedWith"
COL_DEV_TYPE = "DevType"

MULTI_CHOICE_COLUMNS = [
    COL_LANGUAGES,
    "DatabaseHaveWorkedWith",
    "PlatformHaveWorkedWith",
    "WebframeHaveWorkedWith",
]

NUMERIC_COLUMNS = [COL_SALARY, COL_JOB_SAT, COL_YEARS_PRO, COL_YEARS_CODE]

MIN_GROUP_SIZE = 30

FILTER_ALL = "Wszystkie"
PALETTE = "viridis"

REMOTE_ORDER = [
    "Remote",
    "Hybrid (some remote, some in-person)",
    "In-person",
]
