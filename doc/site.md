# Le site : `scripts/build.py` et `templates/page.html`

## Génération

```bash
python scripts/build.py          # valide toutes les éditions et génère docs/
python scripts/build.py --check  # valide seulement, n'écrit rien
```

`build.py` :

1. lit `config/sources.json` et la liste des `id` de rubriques ;
2. charge et valide toutes les éditions de `data/editions/`, dans l'ordre des noms de fichier (voir [format-edition.md](format-edition.md)) ;
3. s'arrête avec le code `1` à la première édition invalide, après avoir listé toutes les erreurs ;
4. numérote les éditions valides à partir de 1 ;
5. écrit une page par édition dans `docs/editions/AAAA-MM-JJ.html` ;
6. écrit la dernière édition dans `docs/index.html` ;
7. crée `docs/.nojekyll` pour que GitHub Pages serve les fichiers tels quels.

Le site est regénéré entièrement à chaque build. `docs/` est ignoré par git : ne le commite jamais.

## Sortie

```text
docs/
├── .nojekyll
├── index.html                  dernière édition
└── editions/
    ├── 2026-11-22.html
    └── …
```

## Le gabarit

`templates/page.html` est un fichier unique avec le HTML, le CSS et le JavaScript inline. `build.py` y remplace deux marqueurs :

| Marqueur | Remplacé par |
| --- | --- |
| `__TITRE__` | `Le Petit Compilé · n° N · AAAA-MM-JJ` |
| `__DATA__` | Les données de la page, en JSON, dans `<script type="application/json" id="data">` |

Le JSON est protégé pour l'intégration dans une balise `<script>` : `</` devient `<\/`, et les séparateurs U+2028 et U+2029 sont échappés.

### Données injectées

```json
{
  "config": {
    "timezone": "Europe/Paris",
    "rubriques": [{"id": "secu", "nom": "Sécurité", "couleur": "#e5484d"}]
  },
  "edition": { "date": "…", "numero": 1, "une": {}, "items": [] },
  "archive": [
    {"numero": 1, "date": "…", "href": "editions/….html",
     "items": [{"rubrique": "…", "titre": "…", "url": "…"}]}
  ],
  "nav": {
    "accueil": "../index.html",
    "precedente": "AAAA-MM-JJ.html",
    "suivante": "AAAA-MM-JJ.html"
  }
}
```

- `archive` contient les `archive_editions` éditions précédant celle affichée, de la plus récente à la plus ancienne.
- Les liens sont relatifs. Depuis `index.html`, ils pointent vers `editions/…` ; depuis une page d'édition, vers le même dossier.
- Sur `index.html`, `nav.accueil` et `nav.suivante` valent `null`.

### Fonctionnement de la page

Le script de la page lit `#data` et construit tout le contenu côté navigateur :

- **Bandeau** « Le Petit Compilé », date et numéro de l'édition.
- **À la une** : grand article, couleur de sa rubrique.
- **Rubriques** dans l'ordre de `config/sources.json`, seulement celles qui ont des articles.
- **Sommaire** : filtres par rubrique avec le nombre d'articles, recherche plein texte dans l'édition, case « Masquer les articles lus ».
- **Articles lus** : bouton par article, et marquage automatique au clic sur le lien.
- **Lien HN** : points et commentaires si `hn` est renseigné.
- **Navigation** entre éditions et **archives** des éditions précédentes.
- **Thème** clair ou sombre : suit le système, ou le choix du lecteur.

### Stockage local

La page garde les préférences du lecteur dans `localStorage`, toujours dans un `try/catch` : elle fonctionne aussi sans stockage.

| Clé | Contenu |
| --- | --- |
| `va-theme` | `light` ou `dark` |
| `va-read` | URL des articles lus (1 500 au plus, les plus anciennes sont retirées) |
| `va-filter` | Filtre de rubrique sélectionné |
| `va-hide` | `1` si les articles lus sont masqués |

### Sécurité du rendu

Tout texte issu des éditions passe par `esc()` avant insertion dans le HTML. Les liens passent par `safeUrl()`, qui remplace toute URL non `http(s)` par `#`. Garde ces deux fonctions pour tout nouveau contenu dynamique.

### Dépendances externes

Seules les polices Google Fonts (Newsreader et Instrument Sans) sont chargées depuis l'extérieur. Sans elles, la page retombe sur les polices système.

## Prévisualiser en local

```bash
python scripts/build.py
python -m http.server 8000 --directory docs
```

Ouvre ensuite `http://localhost:8000/`. Tu peux aussi ouvrir `docs/index.html` directement dans le navigateur : la page n'a besoin d'aucun serveur.
