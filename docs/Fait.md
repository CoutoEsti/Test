# Fait

- Projet cree selon le kit : CLAUDE.md, garde-fou, skill angles-morts, docs, CI.
- Donnees : telechargement Yahoo, copie locale, nettoyage, ecriture tout ou rien, messages d'erreur clairs.
- Pivots confirmes avec test anti-triche (couper le futur ne change pas le passe).
- Strategie Dow version 1 et version 2 (confirmation ^DJI / ^DJT), avec tests anti-triche.
- Backtest : execution au lendemain, frais 0,1 %, comparaison acheter-garder.
- Mesures, tableau, graphique, CSV jour par jour.
- Commande : --robustesse (N de 5 a 30), --confirmation, --test-final (protege).

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
