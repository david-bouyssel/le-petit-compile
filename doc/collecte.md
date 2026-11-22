# Collecte : `scripts/collect.py`

Le script télécharge les flux de [config/sources.json](../config/sources.json) et la une de Hacker News, puis écrit les candidats dans `work/candidates.json`.

## Usage

```bash
python scripts/collect.py            # fenêtre par défaut : window_hours (30 h)
python scripts/collect.py --hours 48 # élargir la fenêtre, par exemple après une panne
```

Sortie console :

```text
412 candidats depuis 33/34 sources -> work/candidates.json
  ECHEC Zataz: URLError: <urlopen error timed out>
  par rubrique : decouvertes=61, dev=40, hn=48, ia=35, ...
```

Code de sortie : `0` si au moins une source répond, `1` si toutes échouent.

## Étapes internes

1. **Lecture de la config** : rubriques, flux, `window_hours`, `max_per_feed`.
2. **Téléchargement parallèle** : 12 threads, délai de 20 s par requête, en-tête `User-Agent` de navigateur.
3. **Analyse des flux** (`parse_feed`) : RSS 2.0 et Atom, sans tenir compte des espaces de noms XML. Pour chaque `item` ou `entry` :
   - `titre` : balise `title`, nettoyée ;
   - `url` : le `link` `rel="alternate"` (Atom) ou le texte de `link` (RSS) ;
   - `extrait` : `description`, `summary`, `content:encoded` ou `content`, sans HTML, coupé à 700 caractères ;
   - `date` : `pubDate`, `published`, `updated` ou `dc:date`, convertie en UTC.
4. **Filtre temporel** : garde les articles postérieurs à `maintenant - window_hours`, ou sans date. Garde au plus `max_per_feed` articles par flux, les plus récents d'abord.
5. **Hacker News** (`collect_hn`) : l'API Algolia renvoie jusqu'à 60 articles de la une, avec points et commentaires.
6. **Déduplication** :
   - les URL des 30 dernières éditions de `data/editions/` sont ignorées ;
   - une URL vue dans deux flux n'est gardée qu'une fois (le premier flux dans l'ordre de la config) ;
   - si une URL d'un flux figure aussi à la une de HN, l'objet `hn` lui est ajouté ;
   - les articles HN restants sont ajoutés avec `rubrique_suggeree: null`.
7. **Tri et numérotation** : du plus récent au plus ancien, identifiants `c001`, `c002`, etc.

## Normalisation des URL

`normalize_url` sert seulement de clé de comparaison. L'URL d'origine reste inchangée dans la sortie. La normalisation :

- force le schéma `https` ;
- met l'hôte en minuscules et retire `www.` ;
- retire le `/` final et le fragment `#…` ;
- retire les paramètres de suivi : `utm_*`, `fbclid`, `gclid`, `mc_*`, `ref`, `ref_src`, `xtor`.

## Format de `work/candidates.json`

```json
{
 "collecte": "2026-11-22T05:00:12+00:00",
 "fenetre_heures": 30,
 "deja_publies_ignores": 41,
 "flux": [
  {"rubrique": "secu", "name": "CERT-FR", "url": "https://…", "ok": true, "count": 3, "error": null},
  {"rubrique": null, "name": "Hacker News (une)", "url": "https://…", "ok": true, "count": 60, "error": null}
 ],
 "candidats": [
  {
   "id": "c001",
   "rubrique_suggeree": "secu",
   "source": "BleepingComputer",
   "titre": "…",
   "url": "https://…",
   "date": "2026-11-22T04:31:00+00:00",
   "extrait": "…",
   "hn": null
  }
 ]
}
```

| Champ | Sens |
| --- | --- |
| `flux[].ok` | `true` si le flux a été téléchargé et analysé |
| `flux[].count` | Nombre d'articles gardés après le filtre temporel |
| `flux[].error` | Type et message de l'erreur, coupés à 200 caractères |
| `candidats[].rubrique_suggeree` | Rubrique du flux d'origine, ou `null` pour la une HN |
| `candidats[].date` | ISO 8601 en UTC, ou `null` si le flux ne date pas ses articles |
| `candidats[].hn` | `{url, points, comments}` si l'article est à la une de HN, sinon `null` |

`work/` est ignoré par git. Le fichier est écrasé à chaque collecte.

## Limites connues

- Un flux qui ne date pas ses articles fournit jusqu'à `max_per_feed` articles à chaque collecte, même anciens. Les articles déjà publiés sont filtrés, mais pas ceux qui ont été écartés.
- Le HTML des extraits est retiré par expressions régulières : quelques résidus restent possibles.
- Aucune nouvelle tentative automatique en cas d'échec réseau. [ROUTINE.md](../ROUTINE.md) demande de relancer une fois si moins de la moitié des sources répondent.
