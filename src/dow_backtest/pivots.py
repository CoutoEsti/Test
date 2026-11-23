"""Sommets et creux CONFIRMES, sans regarder le futur.

Un sommet au jour i : la cloture du jour i est plus haute que les N jours d'avant
(strictement) et au moins aussi haute que les N jours d'apres.
On ne peut le savoir qu'au jour i + N : c'est sa date de confirmation.
Meme logique, inversee, pour un creux.
"""

import pandas as pd

HAUT = "haut"
BAS = "bas"


def trouver_pivots(cloture: pd.Series, fenetre: int) -> pd.DataFrame:
    """Une ligne par pivot : date_pivot, date_confirmation, prix, type (haut / bas).

    Triee par date de confirmation. Les N derniers jours ne peuvent pas encore etre des pivots.
    """
    if fenetre < 1:
        raise ValueError("La fenetre doit etre d'au moins 1 jour.")
    c = cloture.astype(float)
    max_avant = c.shift(1).rolling(fenetre).max()
    min_avant = c.shift(1).rolling(fenetre).min()
    inverse = c[::-1]
    max_apres = inverse.shift(1).rolling(fenetre).max()[::-1]
    min_apres = inverse.shift(1).rolling(fenetre).min()[::-1]

    est_haut = (c > max_avant) & (c >= max_apres)
    est_bas = (c < min_avant) & (c <= min_apres)

    dates = c.index
    lignes = []
    for type_pivot, masque in ((HAUT, est_haut), (BAS, est_bas)):
        for i in masque.to_numpy().nonzero()[0]:
            lignes.append(
                {
                    "date_pivot": dates[i],
                    "date_confirmation": dates[i + fenetre],
                    "prix": c.iloc[i],
                    "type": type_pivot,
                }
            )
    colonnes = ["date_pivot", "date_confirmation", "prix", "type"]
    pivots = pd.DataFrame(lignes, columns=colonnes)
    return pivots.sort_values(["date_confirmation", "type"]).reset_index(drop=True)
