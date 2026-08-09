"""
Fonctions utilitaires utilisées par les générateurs de données.

Ce module centralise les fonctions réutilisables par l'ensemble
des scripts de génération de données.
"""

from __future__ import annotations

from datetime import date, timedelta
import random

from .config import RANDOM_SEED


# ==========================================================
# GÉNÉRATION ALÉATOIRE
# ==========================================================

def set_random_seed() -> None:
    """
    Initialise le générateur de nombres aléatoires.

    L'utilisation d'une graine fixe permet de garantir
    la reproductibilité des données générées.
    """
    random.seed(RANDOM_SEED)


# ==========================================================
# UTILITAIRES DE DATES
# ==========================================================

def generate_dates(start_date: date, end_date: date) -> list[date]:
    """
    Génère toutes les dates comprises entre deux dates incluses.

    Paramètres
    ----------
    start_date : date
        Date de début de la période de génération.

    end_date : date
        Date de fin de la période de génération.

    Retourne
    --------
    list[date]
        Liste contenant toutes les dates générées.
    """
    number_of_days = (end_date - start_date).days + 1

    return [
        start_date + timedelta(days=i)
        for i in range(number_of_days)
    ]


def is_weekend(current_date: date) -> bool:
    """
    Détermine si une date correspond à un jour du week-end.

    Paramètres
    ----------
    current_date : date
        Date à vérifier.

    Retourne
    --------
    bool
        True si la date correspond au samedi ou au dimanche,
        sinon False.
    """
    return current_date.weekday() >= 5


def is_sunday(current_date: date) -> bool:
    """
    Détermine si une date correspond à un dimanche.

    Paramètres
    ----------
    current_date : date
        Date à vérifier.

    Retourne
    --------
    bool
        True si la date correspond à un dimanche,
        sinon False.
    """
    return current_date.weekday() == 6


# ==========================================================
# RÈGLES MÉTIER
# ==========================================================

def apply_saturday_factor(value: float) -> float:
    """
    Réduit l'activité industrielle le samedi.

    L'activité du samedi correspond à 60 % de l'activité
    habituelle.

    Paramètres
    ----------
    value : float
        Valeur à laquelle appliquer le facteur.

    Retourne
    --------
    float
        Valeur ajustée.
    """
    return value * 0.60


def get_season(current_date: date) -> str:
    """
    Détermine la saison météorologique associée à une date.

    Saisons :
        - Winter
        - Spring
        - Summer
        - Autumn

    Paramètres
    ----------
    current_date : date
        Date dont on souhaite déterminer la saison.

    Retourne
    --------
    str
        Saison correspondante.
    """
    month = current_date.month

    if month in (12, 1, 2):
        return "Winter"

    if month in (3, 4, 5):
        return "Spring"

    if month in (6, 7, 8):
        return "Summer"

    return "Autumn"