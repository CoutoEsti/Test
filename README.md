# dow-backtest

Teste la Dow Theory sur l'historique boursier et la compare a "acheter et garder", frais inclus.
Backtest seulement : aucun argent reel, aucun courtier.

## Installer (une fois)
1. Installer uv : https://docs.astral.sh/uv/getting-started/installation/
   (Windows, dans PowerShell : `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`)
2. Dans le dossier du projet : `uv sync`

## Utiliser
| Commande | Ce que ca fait |
|---|---|
| `uv run dow-backtest SPY` | Version 1 sur 1993-2015 : tableau + graphique dans `rapports/` |
| `uv run dow-backtest SPY --confirmation` | Version 2 : industrielles + transports doivent confirmer |
| `uv run dow-backtest SPY --robustesse` | Compare plusieurs tailles de fenetre N |
| `uv run dow-backtest SPY --fenetre 20 --frais 0.002` | Change les reglages pour un essai |
| `uv run dow-backtest SPY --rafraichir` | Re-telecharge les donnees |
| `uv run dow-backtest SPY --test-final` | Periode cachee 2016-aujourd'hui. UNE seule fois. |
| `uv run pytest` | Lance les tests |

Details et decisions : `docs/structure.md`.
