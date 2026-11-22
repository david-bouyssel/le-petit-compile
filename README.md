# veille-auto

Revue de presse tech quotidienne en français, rédigée par une routine Claude dans le cloud et publiée sur GitHub Pages.

## Fonctionnement

1. Chaque jour à 05:00 UTC, une routine Claude Code clone ce dépôt et suit [ROUTINE.md](ROUTINE.md).
2. `scripts/collect.py` lit les flux RSS de [config/sources.json](config/sources.json) et la une de Hacker News, puis écrit les candidats dans `work/candidates.json`.
3. Claude choisit les articles, les lit si besoin et rédige titre, résumé et « pourquoi » en français dans `data/editions/AAAA-MM-JJ.json`.
4. `scripts/build.py` valide les éditions et génère `docs/`.
5. Le commit de l'édition déclenche [publish.yml](.github/workflows/publish.yml), qui publie le site sur GitHub Pages.

## Rubriques

Sécurité, IA et LLM, Dev et programmation, Linux et open source, Découvertes technologiques, Jeux vidéo, Rétro gaming et émulation, Science et espace, Tutos et outils.

Pour ajouter ou retirer une source, modifie `config/sources.json`, puis vérifie avec `python scripts/collect.py`.

## En local

```bash
python scripts/collect.py      # collecte, sans dépendance externe
python scripts/build.py        # valide et génère docs/
python scripts/build.py --check  # valide seulement
```

Python 3.10 ou plus récent, bibliothèque standard uniquement.
