"""Mesures de performance a partir du tableau produit par backtest.lancer."""

import math

import pandas as pd

from dow_backtest import config


def calculer(resultat: pd.DataFrame) -> dict:
    """Rendement total et annuel, pire baisse, volatilite, Sharpe, transactions, temps investi."""
    capital = resultat["capital"]
    rendement = resultat["rendement"]
    if capital.empty:
        raise ValueError("Aucun jour dans le resultat : rien a mesurer.")
    depart = capital.iloc[0] / (1 + rendement.iloc[0])  # capital avant le premier jour
    fin = capital.iloc[-1]
    annees = (capital.index[-1] - capital.index[0]).days / 365.25
    total = fin / depart - 1
    annuel = (fin / depart) ** (1 / annees) - 1 if annees > 0 and fin > 0 else math.nan
    pire_baisse = (capital / capital.cummax().clip(lower=depart) - 1).min()
    ecart_type = rendement.std()
    jours = config.JOURS_BOURSE_PAR_AN
    volatilite = ecart_type * math.sqrt(jours)
    # Sharpe : rendement AU-DESSUS du taux sans risque, divise par le risque.
    excedent = rendement - resultat["taux_jour"] if "taux_jour" in resultat else rendement
    ecart_excedent = excedent.std()
    sharpe = excedent.mean() / ecart_excedent * math.sqrt(jours) if ecart_excedent > 0 else math.nan
    investi = resultat["investi"]
    transactions = int(investi.diff().abs().fillna(0).sum() + investi.iloc[0])
    return {
        "rendement_total": total,
        "rendement_annuel": annuel,
        "pire_baisse": min(pire_baisse, 0.0),
        "volatilite": volatilite,
        "sharpe": sharpe,
        "transactions": transactions,
        "temps_investi": investi.mean(),
        "capital_final": fin,
    }
