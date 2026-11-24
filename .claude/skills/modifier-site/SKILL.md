---
name: modifier-site
description: Modifie le site « Le Petit Compilé » de le-petit-compile - mise en page, styles, thème clair/sombre, filtres, recherche, archives, navigation, titre - dans templates/page.html et scripts/build.py, puis prévisualise le résultat. Utilise cette skill pour toute demande de changement visuel ou fonctionnel du site publié. Ne l'utilise pas pour le contenu d'une édition (skills edition-du-jour et corriger-edition).
---

# Modifier le site

Référence complète : [doc/site.md](../../../doc/site.md).

## Où modifier

| Changement | Fichier |
| --- | --- |
| HTML, CSS, comportement de la page | `templates/page.html` |
| Données transmises à la page, titre de l'onglet, chemins, archives | `scripts/build.py` (`render()`) |
| Nom, couleur ou ordre des rubriques | `config/sources.json` (voir skill `gerer-sources`) |
| Nombre d'éditions archivées | `archive_editions` dans `config/sources.json` |

Le site final est dans `docs/`, généré et ignoré par git. Ne modifie jamais `docs/` à la main.

## Contraintes du gabarit

- Un seul fichier : HTML, CSS et JS restent inline dans `templates/page.html`.
- Les seuls marqueurs remplacés sont `__TITRE__` et `__DATA__`. Garde-les intacts.
- Les données arrivent par `<script type="application/json" id="data">`. Pour une nouvelle donnée, ajoute-la dans le dictionnaire `data` de `render()` dans `build.py`, puis lis-la dans la page.
- Passe tout texte issu des éditions par `esc()` et toute URL par `safeUrl()`.
- Accède à `localStorage` seulement via `store()`, qui gère les erreurs. Préfixe toute nouvelle clé par `va-`.
- Couleurs : définies comme variables CSS sur `:root`, redéfinies pour le mode sombre dans `@media (prefers-color-scheme: dark)` avec `:root:not([data-theme="light"])`, et dans `:root[data-theme="dark"]`. Toute nouvelle couleur suit ce schéma.
- La page doit rester lisible sur mobile (largeur 375 px), sans défilement horizontal.
- Aucune nouvelle dépendance externe : pas de bibliothèque JS, pas de CDN. Exceptions existantes : les polices Google Fonts, et le lecteur `chiptune3` du mod du jour, copié dans `vendor/` (pas de CDN) et chargé seulement au clic.
- Les liens entre pages sont relatifs ; `index.html` est à la racine, les éditions dans `editions/`. Teste les deux.

## Prévisualiser

```bash
python scripts/build.py
python -m http.server 8000 --directory docs
```

Ouvre `http://localhost:8000/` dans le navigateur intégré. Vérifie :

1. `index.html` et une page `editions/AAAA-MM-JJ.html` ;
2. les thèmes clair et sombre (bouton « Clair / sombre ») ;
3. la largeur mobile (375 px) ;
4. les filtres, la recherche, « Masquer les articles lus » et la navigation entre éditions ;
5. la console : aucune erreur JavaScript.

Avec une seule édition, l'archive et la navigation sont vides. Pour tester ces zones, copie temporairement l'édition sous une autre date dans un dossier jetable, jamais dans `data/editions/`. Sinon, signale à l'utilisateur que ces zones n'ont pas été testées.

## Terminer

- `python scripts/build.py --check` doit passer.
- Si le comportement de la page change, mets à jour [doc/site.md](../../../doc/site.md).
- Propose un commit `feat(site): …` ou `fix(site): …`. Le push sur `main` redéploie le site, car `templates/` et `scripts/` sont surveillés par `publish.yml`.
