"""Donnees inventees pour les tests. Jamais d'Internet dans les tests."""

import numpy as np
import pandas as pd
import pytest


def serie(valeurs, debut="2000-01-03") -> pd.Series:
    """Serie de clotures sur des jours ouvrables consecutifs."""
    index = pd.bdate_range(debut, periods=len(valeurs))
    return pd.Series(np.asarray(valeurs, dtype=float), index=index, name="Close")


def marche_aleatoire(n: int, graine: int = 0, debut: str = "2000-01-03") -> pd.Series:
    rng = np.random.default_rng(graine)
    return serie(100 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, n))), debut)


def prix_complets(cloture: pd.Series) -> pd.DataFrame:
    """Tableau Open/High/Low/Close/Volume a partir de clotures."""
    return pd.DataFrame(
        {
            "Open": cloture,
            "High": cloture * 1.01,
            "Low": cloture * 0.99,
            "Close": cloture,
            "Volume": 1_000_000,
        },
        index=cloture.index.rename("Date"),
    )


def zigzag(pas: list[float], longueur: int = 5, depart: float = 100.0) -> pd.Series:
    """Ligne brisee : chaque element de `pas` est un mouvement total sur `longueur` jours."""
    valeurs = [depart]
    for mouvement in pas:
        for _ in range(longueur):
            valeurs.append(valeurs[-1] + mouvement / longueur)
    return serie(valeurs)


@pytest.fixture
def aleatoire():
    return marche_aleatoire(1500)
