# Format d'une édition

Une édition est un fichier `data/editions/AAAA-MM-JJ.json`, encodé en UTF-8, avec des fins de ligne LF. Le nom du fichier est la date de l'édition, dans le fuseau `Europe/Paris`.

## Structure

```json
{
  "date": "2026-11-22",
  "genere": "2026-11-22T06:04:00+01:00",
  "une": { "…article…" },
  "items": [ { "…article…" } ]
}
```

| Champ | Type | Obligatoire | Règle |
| --- | --- | --- | --- |
| `date` | chaîne | oui | Égale au nom du fichier, format `AAAA-MM-JJ` |
| `genere` | chaîne | non (recommandé) | Horodatage ISO 8601 de la rédaction, avec décalage horaire |
| `une` | objet article | oui | L'article principal du jour |
| `items` | liste d'articles | oui, non vide | Les autres articles, rangés par rubrique puis par importance |

`numero` n'est pas stocké : `build.py` le calcule à partir de l'ordre chronologique des éditions valides (la première édition porte le n° 1).

## Article

```json
{
  "rubrique": "secu",
  "source": "BleepingComputer",
  "titre": "Microsoft corrige une faille zero-day d'Exchange exploitée depuis octobre",
  "resume": "Deux à quatre phrases factuelles.",
  "pourquoi": "Une phrase sur l'intérêt concret pour le lecteur.",
  "url": "https://www.bleepingcomputer.com/news/…",
  "date": "2026-11-21T18:12:00+00:00",
  "suite": false,
  "hn": null
}
```

| Champ | Type | Obligatoire | Règle |
| --- | --- | --- | --- |
| `rubrique` | chaîne | oui | Un `id` de `config/sources.json` |
| `source` | chaîne non vide | oui | Nom du média (le `source` du candidat) |
| `titre` | chaîne non vide | oui | Titre informatif en français, sans point final |
| `resume` | chaîne non vide | oui | 2 à 4 phrases ; 4 à 6 pour la une |
| `pourquoi` | chaîne non vide | oui | Une phrase |
| `url` | chaîne | oui | Commence par `http://` ou `https://` ; unique dans l'édition |
| `date` | chaîne ou `null` | non | Date ISO 8601 de l'article d'origine |
| `suite` | booléen | non | `true` si l'article prolonge un sujet d'une édition récente |
| `hn` | objet ou `null` | non | `{url, points, comments}`, `url` sur `https://news.ycombinator.com/` |

Seuls les champs `rubrique`, `source`, `titre`, `resume`, `pourquoi` et `url` sont vérifiés comme obligatoires. Mets quand même toujours `date`, `suite` et `hn` pour garder un format homogène.

## Règles de validation de `build.py`

`build.py` (et `build.py --check`) refuse une édition si :

- le fichier n'est pas du JSON valide ;
- la racine n'est pas un objet ;
- `date` ne vaut pas le nom du fichier, ou le nom ne suit pas `AAAA-MM-JJ` ;
- `une` manque, ou n'est pas un objet ;
- `items` manque, n'est pas une liste, ou est vide ;
- un champ obligatoire d'un article manque, n'est pas une chaîne ou ne contient que des espaces ;
- `rubrique` n'est pas un `id` connu ;
- `url` ne commence pas par `http://` ou `https://` ;
- une `url` apparaît deux fois dans l'édition (une comprise) ;
- `date` n'est ni une chaîne ni `null` ;
- `suite` est présent sans être un booléen ;
- `hn` n'est ni `null` ni un objet dont `url` commence par `https://news.ycombinator.com/`.

Une seule édition invalide fait échouer tout le build : le site n'est pas regénéré. Les erreurs sont listées sur la sortie d'erreur avec le fichier et la position, par exemple :

```text
2 erreur(s) :
  - 2026-11-22.json items[7] : champ « pourquoi » manquant ou vide
  - 2026-11-22.json items[12] : rubrique inconnue « securite » (attendu : decouvertes, dev, ia, jeux, linux, retro, science, secu, tutos)
```

## Ce que la validation ne vérifie pas

Ces points relèvent de la relecture, pas du script :

- l'exactitude des faits par rapport à la source ;
- la longueur du résumé ;
- la présence de l'article de la une dans `items` avec une autre URL ;
- un même sujet traité deux fois avec deux URL différentes ;
- l'ordre des `items`.

## Exemple minimal valide

```json
{
  "date": "2026-11-23",
  "genere": "2026-11-23T06:02:00+01:00",
  "une": {
    "rubrique": "ia",
    "source": "Simon Willison",
    "titre": "…",
    "resume": "…",
    "pourquoi": "…",
    "url": "https://simonwillison.net/2026/Nov/22/…/",
    "date": "2026-11-22T21:40:00+00:00",
    "suite": false,
    "hn": null
  },
  "items": [
    {
      "rubrique": "linux",
      "source": "LinuxFr",
      "titre": "…",
      "resume": "…",
      "pourquoi": "…",
      "url": "https://linuxfr.org/news/…",
      "date": null,
      "suite": false,
      "hn": null
    }
  ]
}
```
