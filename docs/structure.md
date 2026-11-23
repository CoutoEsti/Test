# Structure et decisions

## Structure
```
pyproject.toml          dependances et reglages des outils (uv, pytest, ruff)
uv.lock                 versions exactes installees
CLAUDE.md               regles pour Claude
.claude/                garde-fou (hook) et skill angles-morts
.github/workflows/      CI : ruff + tests a chaque envoi (Linux et Windows)
docs/                   ce fichier, A-faire.md, Fait.md
data/                   copie locale des prix (hors git, re-telechargeable)
rapports/               graphiques et CSV produits (hors git)
src/dow_backtest/
  config.py             SEULE source des reglages
  donnees.py            SEUL endroit qui parle a Yahoo (telechargement, copie locale, nettoyage)
  pivots.py             sommets et creux confirmes
  strategie.py          regles Dow -> investi (1) ou non (0) ; version 2 confirmation
  backtest.py           execution, frais, capital
  mesures.py            rendement, pire baisse, Sharpe, transactions
  rapport.py            tableau texte et graphique
  cli.py                commande dow-backtest
tests/                  un fichier par module, prix inventes, jamais d'Internet
ml/                     notebook existant, hors projet, ne pas toucher
```

## Regles de la strategie (version 1)
- Sommet au jour i : cloture plus haute que les N jours d'avant et au moins egale aux N jours d'apres.
  Connu seulement au jour i + N (confirmation). Creux : l'inverse.
- Achat : dernier creux confirme plus haut que le precedent ET cloture au-dessus du dernier sommet.
- Vente : cloture sous le dernier creux confirme.
- Decision a la cloture du jour t, execution a la cloture du jour t+1, gain compte a partir de t+2.
- Hors du marche : l'argent comptant rapporte le taux ^IRX connu la veille.
- N = 10 par defaut, choisi avant de voir les resultats.

## Version 2 : confirmation
- Signaux calcules sur ^DJI (industrielles) et ^DJT (transports), trade sur SPY.
- Investi quand les deux sont haussiers, sorti quand les deux sont baissiers, sinon on garde.

## Decisions (etape 2, validees par l'utilisateur)
| Sujet | Decision |
|---|---|
| Nom | dow-backtest |
| Marche | SPY (donnees depuis 1993, dividendes inclus via auto_adjust) |
| Unite de temps | Jour |
| Sens | Achat seulement (investi ou en argent comptant) |
| Frais | 0,1 % par achat ou vente |
| Periode de developpement | 1993 a 2015 |
| Periode cachee | 2016 a aujourd'hui, une seule fois, avec --test-final. Robustesse interdite dessus. |
| CI | GitHub Actions, Linux + Windows |
| Outil | uv (MIT/Apache) : memes commandes sur Windows et Linux |
| Librairie de backtest | Aucune, faite maison (backtesting.py est AGPL, et le notre est teste) |
| Interet sur l'argent comptant | Taux des bons du Tresor US 13 semaines (^IRX), celui de la veille. Desactivable : --sans-interet |
| Sharpe | Rendement au-dessus du taux ^IRX, divise par la volatilite |

## Angles morts [TOUS]
| Point | Reponse |
|---|---|
| Secrets | Aucun pour l'instant (yfinance sans cle). .env dans .gitignore. Garde-fou anti-secret. |
| Sauvegardes | Code sur GitHub. Donnees re-telechargeables (--rafraichir). Restauration = effacer data/ et relancer. |
| Performance | Test automatique : 25 000 lignes en moins de 2 s. |
| Retour en arriere | git, un commit par morceau. |
| CI | .github/workflows/ci.yml |
| Documentation | README.md + ce fichier. |
| Publication (type outil ligne de commande) | Pas necessaire : rien n'est publie. |
| Biais du survivant | Pas concerne : SPY est un fonds indiciel, pas une selection d'actions. |

## Test final pre-enregistre (ecrit et commite AVANT de lancer)
- Version officielle : Dow confirmation (^DJI + ^DJT), N=10, frais 0,1 %, interet ^IRX, trade sur SPY.
  Choisie parce qu'elle etait la meilleure sur la periode de developpement (1993-2015).
- Version secondaire rapportee aussi, mais pas choisie apres coup : Dow simple N=10.
- Periode : 2016-01-01 a la derniere donnee disponible.
- Commande : uv run dow-backtest SPY --confirmation --test-final
- Criteres decides avant :
  - "Bat le marche" : rendement par an superieur a acheter-garder.
  - "Meilleur rapport gain / risque" : Sharpe superieur ET pire baisse plus petite qu'acheter-garder.
  - Sinon : la strategie ne vaut pas mieux qu'acheter et garder sur cette periode.
- Apres le test : plus aucun reglage ne change sur la base de ce resultat.
