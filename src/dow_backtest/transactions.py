"""Liste des transactions, taux de reussite, et simulation "risque fixe en $ par transaction".

Une transaction = une periode continue ou l'on est investi.
- Achat a la cloture de la veille du premier jour investi (au 1er jour evalue si deja investi).
- Vente a la cloture du dernier jour investi. Encore investi a la fin : "ouverte", evaluee au
  dernier prix.
- Stop = dernier creux confirme connu le jour de la DECISION (veille de l'achat).
  Taille = risque en $ / (prix d'achat - stop). La vraie perte peut depasser le risque prevu :
  on vend le lendemain du signal, au prix du jour, pas exactement au stop.
"""

import math

import pandas as pd

from dow_backtest import config


def extraire(
    cloture: pd.Series,
    resultat: pd.DataFrame,
    stops: pd.Series,
    frais: float = config.FRAIS_PAR_TRANSACTION,
    risque: float = config.RISQUE_PAR_TRANSACTION,
) -> pd.DataFrame:
    """Une ligne par transaction. `cloture` et `stops` couvrent tout l'historique."""
    investi = resultat["investi"].to_numpy()
    jours = resultat.index
    position = {d: i for i, d in enumerate(cloture.index)}
    lignes = []
    debut = None
    for k in range(len(investi)):
        if investi[k] == 1 and debut is None:
            debut = k
        fin_de_periode = k == len(investi) - 1
        if debut is not None and (fin_de_periode or investi[k + 1] == 0):
            i_achat = position[jours[debut]] - (1 if debut > 0 else 0)
            i_vente = position[jours[k]]
            prix_achat = float(cloture.iloc[i_achat])
            prix_vente = float(cloture.iloc[i_vente])
            stop = float(stops.iloc[i_achat - 1]) if i_achat > 0 else math.nan
            par_part = prix_achat - stop
            parts = risque / par_part if par_part > 0 else math.nan
            frais_dollars = parts * (prix_achat + prix_vente) * frais
            gain = parts * (prix_vente - prix_achat) - frais_dollars
            lignes.append(
                {
                    "date_achat": cloture.index[i_achat],
                    "prix_achat": prix_achat,
                    "date_vente": cloture.index[i_vente],
                    "prix_vente": prix_vente,
                    "jours": i_vente - i_achat,
                    "rendement": prix_vente / prix_achat * (1 - frais) ** 2 - 1,
                    "ouverte": fin_de_periode and investi[k] == 1,
                    "stop": stop,
                    "montant_investi": parts * prix_achat,
                    "gain_dollars": gain,
                    "gain_R": gain / risque,
                }
            )
            debut = None
    return pd.DataFrame(lignes)


def statistiques(transactions: pd.DataFrame, risque: float = config.RISQUE_PAR_TRANSACTION) -> dict:
    """Taux de reussite, gains et pertes moyens, facteur de profit, resultat en $."""
    if transactions.empty:
        return {"transactions": 0}
    r = transactions["rendement"]
    gagnantes, perdantes = r[r > 0], r[r <= 0]
    g = transactions["gain_dollars"].dropna()
    cumul = g.cumsum()
    pire_baisse_dollars = (cumul - cumul.cummax().clip(lower=0)).min() if len(g) else math.nan
    somme_pertes = -g[g < 0].sum()
    return {
        "transactions": len(transactions),
        "taux_reussite": len(gagnantes) / len(r),
        "gain_moyen": gagnantes.mean() if len(gagnantes) else math.nan,
        "perte_moyenne": perdantes.mean() if len(perdantes) else math.nan,
        "meilleure": r.max(),
        "pire": r.min(),
        "jours_moyens": transactions["jours"].mean(),
        "facteur_profit": g[g > 0].sum() / somme_pertes if somme_pertes > 0 else math.nan,
        "risque": risque,
        "total_dollars": g.sum(),
        "R_moyen": transactions["gain_R"].mean(),
        "pire_R": transactions["gain_R"].min(),
        "pertes_au_dela_du_risque": int((transactions["gain_R"] < -1).sum()),
        "pire_baisse_dollars": min(pire_baisse_dollars, 0.0),
        "plus_gros_montant": transactions["montant_investi"].max(),
    }


def texte(stats: dict) -> str:
    """Resume lisible des statistiques."""
    if stats["transactions"] == 0:
        return "Aucune transaction."
    s = stats
    return "\n".join(
        [
            f"Transactions                {s['transactions']}",
            f"Taux de reussite            {s['taux_reussite']:.1%}",
            f"Gain moyen (gagnantes)      {s['gain_moyen']:+.1%}",
            f"Perte moyenne (perdantes)   {s['perte_moyenne']:+.1%}",
            f"Meilleure / pire            {s['meilleure']:+.1%} / {s['pire']:+.1%}",
            f"Duree moyenne               {s['jours_moyens']:.0f} jours de bourse",
            f"Facteur de profit           {s['facteur_profit']:.2f}  (gains $ / pertes $)",
            "",
            f"Avec {s['risque']:.0f} $ de risque par transaction (stop = dernier creux) :",
            f"  Resultat total            {s['total_dollars']:+,.0f} $",
            f"  Moyenne par transaction   {s['R_moyen']:+.2f} R  (1 R = {s['risque']:.0f} $)",
            f"  Pire transaction          {s['pire_R']:+.2f} R",
            f"  Pertes plus grandes que le risque prevu : {s['pertes_au_dela_du_risque']}",
            f"  Pire baisse du cumul      {s['pire_baisse_dollars']:+,.0f} $",
            f"  Plus gros montant investi {s['plus_gros_montant']:,.0f} $ (sur une transaction)",
        ]
    )
