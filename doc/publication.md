# Publication et automatisation

## La routine Claude Code

Une routine Claude Code planifiée dans le cloud produit l'édition chaque jour à **05:00 UTC**, soit 06:00 à Paris en hiver et 07:00 en été.

À chaque exécution, elle :

1. clone le dépôt ;
2. lit et suit [ROUTINE.md](../ROUTINE.md), étape par étape ;
3. pousse un seul commit, `chore(edition): édition du AAAA-MM-JJ`, qui ajoute `data/editions/AAAA-MM-JJ.json` ;
4. termine par un compte rendu : articles par rubrique, titre de la une, sources en échec.

La routine se gère depuis claude.ai (Claude Code, routines) ou avec la commande `/schedule` de Claude Code. Le prompt de la routine doit seulement demander de suivre `ROUTINE.md` : toutes les consignes vivent dans le dépôt, versionnées avec le code.

### Règles imposées à la routine

- Ne pas modifier `scripts/`, `templates/`, `config/` ni `ROUTINE.md`.
- Ne commiter que le fichier de l'édition.
- S'arrêter si l'édition du jour existe déjà : une relance le même jour ne fait rien.

## Workflow `publish.yml`

Déclencheurs :

- un push sur `main` ou `claude/**` qui touche `data/editions/`, `scripts/`, `templates/`, `config/`, `vendor/` ou le workflow lui-même ;
- un lancement manuel (`workflow_dispatch`).

Les exécutions d'une même branche passent l'une après l'autre (`concurrency`, sans annulation).

### Job `merge` (branche autre que `main`)

La routine cloud peut n'avoir le droit de pousser que sur une branche `claude/*`. Dans ce cas, le job :

1. fusionne la branche dans `main`, en avance rapide si possible, sinon avec un commit de fusion ;
2. pousse `main` ;
3. supprime la branche distante ;
4. relance `publish.yml` sur `main` avec `gh workflow run`.

La relance explicite est nécessaire : un push fait avec `GITHUB_TOKEN` ne déclenche pas d'autre workflow. De plus, l'environnement `github-pages` n'accepte que les déploiements depuis `main`.

### Jobs `build` puis `deploy` (branche `main`)

1. `build` : `python3 scripts/build.py` (validation et génération de `docs/`), `actions/configure-pages`, puis `actions/upload-pages-artifact` (dossier `docs`).
2. `deploy` : `actions/deploy-pages`, une fois `build` terminé.

Les deux étapes sont dans deux jobs, comme le recommande GitHub. Dans un seul job, `deploy-pages` cherchait parfois l'artefact quelques dixièmes de seconde après son envoi, avant qu'il soit visible, et échouait avec « No artifacts named "github-pages" were found ».

Si une édition est invalide, le build échoue et le site en ligne reste sur la version précédente.

## Workflow `cleanup.yml`

Chaque jour à 06:30 UTC, il supprime les branches distantes `claude/*` déjà contenues dans `main`, et garde celles qui ont des commits absents de `main`. Il se lance aussi à la main.

## Configuration GitHub requise

- **Settings > Pages > Source** : « GitHub Actions ».
- **Settings > Actions > General > Workflow permissions** : lecture et écriture, pour que `merge` puisse pousser sur `main` et supprimer des branches.
- Si `main` est protégée, autorise `github-actions[bot]` à y pousser, ou le job `merge` échouera.

## Publier à la main

Depuis un poste local, après avoir écrit et validé une édition :

```bash
python scripts/build.py
git add data/editions/AAAA-MM-JJ.json
git commit -m "chore(edition): édition du AAAA-MM-JJ"
git push origin main
```

Pour redéployer sans nouveau commit, par exemple après un échec passager de Pages :

```bash
gh workflow run publish.yml --ref main
```
