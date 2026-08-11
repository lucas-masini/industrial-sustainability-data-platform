"""
Configuration de la connexion à MySQL.

"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


# ==========================================================
# CHEMIN DU PROJET
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ==========================================================
# VARIABLES D'ENVIRONNEMENT
# ==========================================================

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# ==========================================================
# CONFIGURATION MYSQL
# ==========================================================

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv(
    "MYSQL_DATABASE",
    "helios_industrial_group",
)


# ==========================================================
# VALIDATION DE LA CONFIGURATION
# ==========================================================

if not MYSQL_PASSWORD:
    raise ValueError(
        "La variable MYSQL_PASSWORD est absente du fichier .env."
    )