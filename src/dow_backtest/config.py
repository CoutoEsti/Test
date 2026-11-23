"""SEULE source des reglages du projet. Ne pas repeter ces valeurs ailleurs."""

from pathlib import Path

# Marche
SYMBOLE_DEFAUT = "SPY"
INDICES_DOW = ("^DJI", "^DJT")  # Industrielles et Transports (version 2 : confirmation)
SYMBOLE_TAUX = "^IRX"  # Taux des bons du Tresor US 13 semaines (en %, annuel)

# Periodes
DEBUT_DEVELOPPEMENT = "1993-01-01"
FIN_DEVELOPPEMENT = "2015-12-31"
DEBUT_TEST_FINAL = "2016-01-01"  # Periode cachee : a regarder UNE seule fois

# Strategie
FENETRE_PIVOT = 10  # N jours de chaque cote pour qu'un sommet / creux soit reconnu
FENETRES_ROBUSTESSE = (5, 10, 15, 20, 25, 30)

# Backtest
FRAIS_PAR_TRANSACTION = 0.001  # 0,1 % du montant a chaque achat ou vente
CAPITAL_INITIAL = 10_000.0
JOURS_BOURSE_PAR_AN = 252

# Dossiers (relatifs au dossier ou la commande est lancee)
DOSSIER_DONNEES = Path("data")
DOSSIER_RAPPORTS = Path("rapports")
