# Fait

- Projet cree selon le kit : CLAUDE.md, garde-fou, skill angles-morts, docs, CI.
- Donnees : telechargement Yahoo, copie locale, nettoyage, ecriture tout ou rien, messages d'erreur clairs.
- Pivots confirmes avec test anti-triche (couper le futur ne change pas le passe).
- Strategie Dow version 1 et version 2 (confirmation ^DJI / ^DJT), avec tests anti-triche.
- Backtest : execution au lendemain, frais 0,1 %, comparaison acheter-garder.
- Mesures, tableau, graphique, CSV jour par jour.
- Commande : --robustesse (N de 5 a 30), --confirmation, --test-final (protege).

- Transactions : taux de reussite, facteur de profit, simulation 100 $ de risque par transaction.
- Interet sur l'argent comptant (^IRX, taux de la veille) et Sharpe au-dessus du taux sans risque.

## Premiers resultats SANS interet (1993 a 2015, SPY, frais 0,1 %, Sharpe sans taux)
| | Dow N=10 | Dow confirmation | Acheter-garder |
|---|---|---|---|
| Rendement par an | 2,7 % | 4,9 % | 8,9 % |
| Pire baisse | -21,5 % | -23,5 % | -55,2 % |
| Sharpe | 0,33 | 0,58 | 0,55 |
| Temps investi | 42,5 % | 44,4 % | 100 % |

Lecture : la Dow Theory rapporte moins, mais evite les grosses baisses (2000-2002, 2008).
Robustesse : les resultats changent beaucoup selon N (0,5 %/an a N=5, 5,5 %/an a N=30).
Choisir N d'apres ce tableau serait du surajustement : N=10 reste le reglage officiel.

## Resultats AVEC interet ^IRX (1993 a 2015, SPY, frais 0,1 %)
| | Dow N=10 | Dow confirmation | Acheter-garder |
|---|---|---|---|
| Rendement par an | 4,2 % | 6,2 % | 8,9 % |
| Pire baisse | -21,5 % | -18,1 % | -55,2 % |
| Sharpe (au-dessus du taux) | 0,22 | 0,43 | 0,41 |
| Temps investi | 42,5 % | 44,4 % | 100 % |

## Autres marches (version 1, N=10, avec interet, du debut des donnees a 2015)
Reproduire une ligne : `uv run dow-backtest QQQ` (remplacer le symbole).
| Marche | Debut | Dow / an | Acheter-garder / an | Pire baisse Dow | Pire baisse A-G | Sharpe Dow | Sharpe A-G |
|---|---|---|---|---|---|---|---|
| S&P 500 SPY | 1993 | 4,2 % | 8,9 % | -21,5 % | -55,2 % | 0,22 | 0,41 |
| Dow Jones DIA | 1998 | 5,3 % | 6,9 % | -17,0 % | -51,9 % | 0,43 | 0,34 |
| Nasdaq 100 QQQ | 1999 | 7,1 % | 5,3 % | -25,8 % | -83,0 % | 0,43 | 0,26 |
| Petites entreprises IWM | 2000 | 6,1 % | 7,1 % | -19,6 % | -58,6 % | 0,43 | 0,34 |
| Canada EWC | 1996 | 6,2 % | 7,2 % | -23,1 % | -60,8 % | 0,36 | 0,32 |
| Hors US EFA | 2001 | 5,1 % | 4,9 % | -15,5 % | -61,0 % | 0,41 | 0,27 |
| Japon EWJ | 1996 | 2,7 % | 0,1 % | -23,9 % | -58,9 % | 0,09 | 0,04 |
| S&P 500 ^GSPC (sans dividendes) | 1927 | 4,2 % | 5,5 % | -48,3 % | -86,2 % | 0,16 | 0,22 |

Lecture : la strategie gagne seulement quand la periode contient un long marche baissier
(depart juste avant 2000, Japon). Elle reduit toujours beaucoup la pire baisse.
Sur un marche qui monte regulierement, elle rapporte moins.

## TEST FINAL (periode cachee 2016-01-04 a 2026-11-20, lance une seule fois le 2026-11-23)
Pre-enregistrement : docs/structure.md, commit 95385a3, pousse AVANT le lancement.

| | Dow confirmation (officielle) | Dow simple N=10 (secondaire) | Acheter-garder |
|---|---|---|---|
| Rendement par an | 4,9 % | 8,2 % | 13,8 % |
| Pire baisse | -21,1 % | -10,7 % | -33,7 % |
| Sharpe | 0,32 | 0,61 | 0,69 |
| Taux de reussite | 61,5 % (13 transactions) | 71,4 % (14) | - |
| 100 $ de risque par transaction | +1 453 $ (+1,12 R en moyenne) | +2 013 $ (+1,44 R) | - |
| Plus gros montant investi | 7 382 $ | 4 825 $ | - |

Verdict selon les criteres decides avant :
- Bat le marche : NON (4,9 % contre 13,8 % par an).
- Meilleur rapport gain / risque : NON (Sharpe 0,32 contre 0,69, meme si la pire baisse est plus petite).
- Conclusion : sur 2016-2026, la Dow Theory ne vaut pas mieux qu'acheter et garder SPY.
- La version simple a fait mieux que la version officielle sur cette periode. On ne change PAS
  de version apres coup : ce serait choisir avec la reponse sous les yeux.
