"""Regles de la Dow Theory -> investi (1) ou pas (0), jour par jour.

Au jour t, on ne connait que les pivots confirmes au plus tard au jour t.
- H1, H0 : dernier et avant-dernier sommets confirmes. L1, L0 : idem pour les creux.
- ACHAT : creux plus haut que le precedent (L1 > L0) ET cloture au-dessus du dernier sommet (> H1).
  C'est un "sommet plus haut + creux plus haut" : tendance haussiere.
- VENTE : cloture sous le dernier creux confirme (< L1). Le creux plus bas commence.
- Sinon : on garde la position de la veille.
La valeur du jour t est la decision prise a la cloture du jour t.
"""

import numpy as np
import pandas as pd

from dow_backtest.pivots import BAS, HAUT, trouver_pivots


def _derniers_niveaux(pivots: pd.DataFrame, type_pivot: str, index: pd.Index):
    """Pour chaque jour : prix du dernier et de l'avant-dernier pivot confirme de ce type."""
    p = pivots[pivots["type"] == type_pivot]
    dernier = pd.Series(p["prix"].to_numpy(), index=p["date_confirmation"])
    precedent = dernier.shift(1)
    dernier = dernier.reindex(index).ffill()
    precedent = precedent.reindex(index).ffill()
    return dernier.to_numpy(), precedent.to_numpy()


def etat_tendance(cloture: pd.Series, fenetre: int) -> pd.Series:
    """1 = tendance haussiere selon Dow, 0 = sinon. Decision a la cloture de chaque jour."""
    pivots = trouver_pivots(cloture, fenetre)
    h1, _ = _derniers_niveaux(pivots, HAUT, cloture.index)
    l1, l0 = _derniers_niveaux(pivots, BAS, cloture.index)
    c = cloture.to_numpy(dtype=float)

    # Les comparaisons avec NaN donnent False : pas de signal tant qu'il manque des pivots.
    achat = (l1 > l0) & (c > h1)
    vente = c < l1

    etat = np.zeros(len(c), dtype=int)
    courant = 0
    for t in range(len(c)):
        if courant == 0 and achat[t]:
            courant = 1
        elif courant == 1 and vente[t]:
            courant = 0
        etat[t] = courant
    return pd.Series(etat, index=cloture.index, name="position")


def confirmation(etat_a: pd.Series, etat_b: pd.Series) -> pd.Series:
    """Version 2 : les deux indices doivent se confirmer.

    Investi quand les deux sont haussiers, sorti quand les deux sont baissiers,
    sinon on garde la position de la veille.
    """
    a, b = etat_a.align(etat_b, join="inner")
    av, bv = a.to_numpy(), b.to_numpy()
    resultat = np.zeros(len(av), dtype=int)
    courant = 0
    for t in range(len(av)):
        if av[t] == 1 and bv[t] == 1:
            courant = 1
        elif av[t] == 0 and bv[t] == 0:
            courant = 0
        resultat[t] = courant
    return pd.Series(resultat, index=a.index, name="position")
