# Dépannage

## Collecte

### Beaucoup de sources en `ECHEC`

- `URLError` ou `timed out` sur presque toutes les sources : le réseau sortant est bloqué ou instable. Relance une fois. Dans la routine cloud, vérifie que l'environnement autorise l'accès réseau.
- `HTTPError: HTTP Error 403` sur une source : le site bloque les robots. Cherche un autre flux du même média, ou retire la source.
- `HTTPError: HTTP Error 404` : l'URL du flux a changé. Cherche la nouvelle dans le code de la page d'accueil du site.
- `ParseError` : le flux renvoie du HTML (page d'erreur, mur de cookies) ou un XML invalide. Ouvre l'URL avec `curl -sL` pour voir la réponse.

Voir [sources.md](sources.md) pour tester et remplacer un flux.

### Une source répond mais `count` vaut 0

Le site n'a rien publié pendant la fenêtre de `window_hours`. Vérifie avec une fenêtre plus large :

```bash
python scripts/collect.py --hours 168
```

Si `count` reste à 0, les dates du flux sont peut-être dans un format non reconnu, ou dans le futur.

### Trop peu de candidats après une panne de plusieurs jours

Élargis la fenêtre de collecte pour rattraper :

```bash
python scripts/collect.py --hours 72
```

## Validation

### `build.py` liste des erreurs

Chaque ligne donne le fichier, la position et la cause. Les causes et les règles sont décrites dans [format-edition.md](format-edition.md). Erreurs fréquentes :

| Message | Correction |
| --- | --- |
| `JSON invalide (Expecting ',' delimiter…)` | Virgule manquante ou guillemet non échappé dans un texte. Remplace les guillemets droits dans le texte par « » ou échappe-les en `\"`. |
| `« date » doit valoir « … »` | Mets dans `date` exactement le nom du fichier. |
| `rubrique inconnue « … »` | Utilise un `id` de `config/sources.json`, pas un nom (`secu`, pas `Sécurité`). |
| `champ « … » manquant ou vide` | Remplis le champ, ou retire l'article. |
| `url en double` | Retire le doublon. Vérifie aussi que la une n'est pas répétée dans `items`. |
| `hn doit être null ou {url, points, comments}` | Recopie l'objet `hn` du candidat tel quel, ou mets `null`. |

### Une ancienne édition devient invalide

Cela arrive après la suppression ou le renommage d'une rubrique dans `config/sources.json`. Rétablis l'`id`, ou corrige les éditions concernées (voir [sources.md](sources.md)).

## Publication

### L'édition est commitée mais le site n'a pas changé

1. Ouvre l'onglet Actions du dépôt et regarde la dernière exécution de « Publier la veille ».
2. Job `merge` en échec : la branche `claude/*` est en conflit avec `main`, ou `main` refuse le push du bot. Fusionne à la main, ou ajuste la protection de branche.
3. Job `publish` en échec à « Générer le site » : une édition est invalide. Lance `python scripts/build.py` en local pour voir l'erreur.
4. Job `publish` en échec au déploiement : vérifie que Pages a bien la source « GitHub Actions ». Relance avec `gh workflow run publish.yml --ref main`.
5. Aucune exécution : le commit ne touche aucun chemin surveillé, ou il a été poussé avec un jeton qui ne déclenche pas de workflow.

### Des branches `claude/*` s'accumulent

`cleanup.yml` garde les branches qui contiennent des commits absents de `main`. Regarde leur contenu : soit la fusion a échoué (voir plus haut), soit la branche contient un travail non publié.

### Deux éditions le même jour

Impossible par construction : la routine s'arrête si le fichier du jour existe. Si deux branches `claude/*` proposent le même fichier, la seconde fusion produit un conflit dans `merge` ; garde une seule version.

## Contenu

### Une erreur factuelle a été publiée

Corrige le texte dans `data/editions/AAAA-MM-JJ.json`, valide, puis commite avec un message du type `fix(edition): corrige le résumé de … du AAAA-MM-JJ`. Le site se redéploie au push. La skill `corriger-edition` décrit la marche à suivre.

### Le même sujet revient chaque jour

`collect.py` ne filtre que les URL identiques. Pour un sujet repris par d'autres sources, la sélection doit le repérer via les titres des 14 dernières éditions et ne le republier qu'avec un fait nouveau et `"suite": true`.
