# Sources et rubriques : `config/sources.json`

Ce fichier pilote la collecte, la validation et l'affichage. Il est lu par `collect.py`, `build.py` et, indirectement, par la page.

## Réglages globaux

| Clé | Défaut | Utilisée par | Effet |
| --- | --- | --- | --- |
| `timezone` | `Europe/Paris` | page | Fuseau d'affichage des dates |
| `window_hours` | `30` | `collect.py` | Âge maximal des articles candidats |
| `max_per_feed` | `15` | `collect.py` | Nombre maximal d'articles par flux |
| `archive_editions` | `14` | `build.py` | Nombre d'éditions précédentes listées en bas de page |
| `hacker_news.front_page` | URL Algolia | `collect.py` | Requête de la une de Hacker News |

## Rubriques

Chaque rubrique est un objet :

```json
{
  "id": "secu",
  "nom": "Sécurité",
  "couleur": "#e5484d",
  "cible": "4 à 6",
  "feeds": [
    {"name": "CERT-FR", "url": "https://www.cert.ssi.gouv.fr/alerte/feed/"}
  ]
}
```

| Champ | Rôle |
| --- | --- |
| `id` | Identifiant court, utilisé dans `rubrique` des éditions. Ne le renomme pas : les anciennes éditions deviendraient invalides. |
| `nom` | Libellé affiché sur le site |
| `couleur` | Couleur d'accent de la rubrique (hexadécimal) |
| `cible` | Nombre d'articles visé, lu par Claude lors de la sélection |
| `feeds` | Liste des flux : `name` (affiché comme source) et `url` (RSS ou Atom) |

L'ordre des rubriques dans le fichier est l'ordre d'affichage sur le site. L'ordre des flux compte aussi : en cas de doublon d'URL entre deux flux, `collect.py` garde le premier.

### Rubriques actuelles

| id | Nom | Cible | Flux |
| --- | --- | --- | --- |
| `secu` | Sécurité | 4 à 6 | The Hacker News, BleepingComputer, CERT-FR, Zataz |
| `ia` | IA et LLM | 4 à 6 | Simon Willison, The Decoder, Hugging Face Blog, ActuIA |
| `dev` | Dev et programmation | 4 à 6 | Lobsters, Journal du Hacker, Developpez.com |
| `linux` | Linux et open source | 2 à 4 | LinuxFr, Linuxiac, Phoronix, OMG! Ubuntu |
| `decouvertes` | Découvertes technologiques | 3 à 5 | Numerama, Korben, Ars Technica, The Verge, Frandroid |
| `jeux` | Jeux vidéo | 3 à 5 | Gematsu, Eurogamer, Rock Paper Shotgun, Gamekult |
| `retro` | Rétro gaming et émulation | 2 à 4 | Time Extension, RetroRGB, Retro Dodo, Libretro, HN « decompilation » |
| `science` | Science et espace | 2 à 4 | Futura, Space.com, Sciences et Avenir |
| `tutos` | Tutos et outils | 3 à 6 | Show HN (50 points et plus), Hacker News « tutorial » (30 points et plus), HN « LLM », « agents/MCP/RAG », « self-hosted/Docker » |

## Ajouter une source

1. Trouve l'URL du flux. Cherche `<link rel="alternate" type="application/rss+xml">` dans le code de la page, ou essaie `/feed`, `/rss`, `/atom.xml`, `/feed.xml`.
2. Vérifie qu'il répond et qu'il contient des articles datés :

   ```bash
   curl -sL -A "Mozilla/5.0" "https://exemple.org/feed" | head -40
   ```

3. Ajoute `{"name": "…", "url": "…"}` dans les `feeds` de la bonne rubrique. Le `name` apparaît sur le site : utilise le nom usuel du média.
4. Lance la collecte et lis la ligne du flux :

   ```bash
   python scripts/collect.py
   python -c "import json;[print(f) for f in json.load(open('work/candidates.json',encoding='utf-8'))['flux'] if f['name']=='Mon média']"
   ```

5. `ok: true` avec `count` supérieur à 0 : la source fonctionne. `count: 0` peut être normal si le site n'a rien publié depuis 30 heures ; relance avec `--hours 168` pour vérifier.

## Retirer une source

Supprime son entrée dans `feeds`. Les éditions passées gardent leur champ `source` : rien d'autre à changer.

## Ajouter une rubrique

1. Ajoute un objet dans `rubriques`, à la position voulue sur le site. Choisis un `id` court, en minuscules, sans accent.
2. Choisis une `couleur` lisible sur fond clair et sur fond sombre.
3. Mets à jour la liste des `id` dans [ROUTINE.md](../ROUTINE.md) (étape 5) et la liste des rubriques du [README](../README.md). Garde le total des `cible` entre 25 et 40.
4. Lance `python scripts/build.py --check` : les anciennes éditions doivent rester valides.

## Supprimer ou renommer une rubrique

`build.py` rejette toute édition qui cite un `id` inconnu. Avant de supprimer ou de renommer un `id`, cherche-le dans les éditions :

```bash
grep -l '"rubrique": "ancien_id"' data/editions/*.json
```

Si des éditions l'utilisent, garde la rubrique avec `"feeds": []`, ou migre ces éditions vers le nouvel `id`. Changer seulement `nom` ou `couleur` est sans risque.
