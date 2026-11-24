# Documentation de le-petit-compile

le-petit-compile produit **Le Petit Compilé**, une revue de presse tech quotidienne en français. Une routine Claude Code dans le cloud collecte les flux, choisit et résume les articles, puis publie le site sur GitHub Pages.

Cette documentation décrit le fonctionnement complet du projet. Pour un aperçu rapide, lis d'abord le [README du dépôt](../README.md).

## Sommaire

| Document | Contenu |
| --- | --- |
| [architecture.md](architecture.md) | Vue d'ensemble, arborescence, flux de données de bout en bout |
| [collecte.md](collecte.md) | `scripts/collect.py` : flux RSS, Hacker News, déduplication, format de `work/candidates.json` |
| [sources.md](sources.md) | `config/sources.json` : rubriques, flux, réglages globaux, ajout ou retrait d'une source |
| [format-edition.md](format-edition.md) | Schéma complet d'une édition `data/editions/AAAA-MM-JJ.json` et règles de validation |
| [redaction.md](redaction.md) | Ligne éditoriale : sélection, tri, rédaction des titres et résumés |
| [site.md](site.md) | `scripts/build.py` et `templates/page.html` : génération et fonctionnement de la page |
| [publication.md](publication.md) | Routine cloud, workflows GitHub Actions, GitHub Pages, branches `claude/*` |
| [depannage.md](depannage.md) | Erreurs fréquentes et solutions |

## Fichiers d'instructions pour Claude

| Fichier | Rôle |
| --- | --- |
| [ROUTINE.md](../ROUTINE.md) | Consignes suivies chaque matin par la routine cloud. Source de vérité pour l'édition quotidienne. |
| [CLAUDE.md](../CLAUDE.md) | Contexte du projet chargé à chaque session Claude Code locale |
| [.claude/skills/](../.claude/skills/) | Skills du projet, une par tâche récurrente (voir ci-dessous) |

| Skill | Quand l'utiliser |
| --- | --- |
| `edition-du-jour` | Produire l'édition du jour à la main, hors routine |
| `corriger-edition` | Corriger une édition invalide ou erronée (validation, faits, doublons) |
| `gerer-sources` | Ajouter, retirer, tester ou réparer un flux RSS ou une rubrique |
| `modifier-site` | Modifier la mise en page ou le comportement du site |

## Prérequis

- Python 3.10 ou plus récent. Les scripts n'utilisent que la bibliothèque standard.
- Git, et un accès en écriture au dépôt pour publier.
- Un accès réseau sortant vers les flux RSS et `hn.algolia.com` pour la collecte.
