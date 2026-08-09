from pathlib import Path
from datetime import date


# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


# ==========================================================
# DATA GENERATION
# ==========================================================

START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 12, 31)

RANDOM_SEED = 42


# ==========================================================
# REFERENCE DATA
# ==========================================================

NB_SITES = 5
NB_PRODUCTS = 10
NB_SUPPLIERS = 8
NB_TRANSPORT_COMPANIES = 5
NB_ENERGY_SOURCES = 5