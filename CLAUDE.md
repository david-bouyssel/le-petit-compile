# le-petit-compile : Le Petit Compilé

Revue de presse tech quotidienne en français. Une routine Claude Code cloud collecte des flux RSS, rédige une édition JSON et publie un site statique sur GitHub Pages. Documentation complète dans [doc/](doc/README.md).

## Repères

- `config/sources.json` : rubriques, flux, réglages. Les `id` de rubrique sont référencés par toutes les éditions.
- `scripts/collect.py` : collecte vers `work/candidates.json` (ignoré par git).
- `scripts/build.py` : valide `data/editions/*.json` et génère `docs/` (ignoré par git).
- `templates/page.html` : gabarit unique, HTML, CSS et JS inline. Marqueurs `__TITRE__` et `__DATA__`.
- `data/editions/AAAA-MM-JJ.json` : une édition par jour, seul contenu produit chaque jour.
- `ROUTINE.md` : consignes de la routine quotidienne. Source de vérité pour la production d'une édition.

`docs/` est la sortie du site. La documentation est dans `doc/`.

## Commandes

```bash
python scripts/collect.py            # collecte (option --hours N)
python scripts/build.py --check      # valide les éditions sans rien écrire
python scripts/build.py              # valide et génère docs/
python -m http.server 8000 --directory docs   # prévisualise le site
```

Lance `python scripts/build.py --check` après toute modification de `data/`, `config/` ou `scripts/build.py`.

## Règles

- Bibliothèque standard Python uniquement, Python 3.10 ou plus récent. Pas de dépendance à installer.
- Textes, commentaires, messages et documentation en français.
- Fichiers en UTF-8 avec fins de ligne LF (voir `.gitattributes`).
- Ne commite jamais `docs/` ni `work/`.
- Ne renomme ni ne supprime un `id` de rubrique utilisé par une édition existante : `build.py` rejetterait l'édition.
- Dans `templates/page.html`, passe tout texte dynamique par `esc()` et toute URL par `safeUrl()`. Enveloppe chaque accès à `localStorage` dans un `try/catch` (fonction `store()`).
- Dans une édition, n'écris que des faits présents dans la source. N'invente jamais un chiffre, une date, une citation ou un nom.
- Si tu changes le comportement de la routine, du format d'édition ou des rubriques, mets à jour `ROUTINE.md` et la page concernée de `doc/`.
- Commits au format Conventional Commits : `chore(edition): édition du AAAA-MM-JJ` pour une édition, `fix(edition): …` pour une correction, `feat(site): …`, `docs: …`, etc.

## Skills du projet

- `edition-du-jour` : produire l'édition du jour à la main.
- `corriger-edition` : corriger une édition invalide ou erronée.
- `gerer-sources` : ajouter, retirer, tester ou réparer un flux ou une rubrique.
- `modifier-site` : changer la mise en page ou le comportement du site.
