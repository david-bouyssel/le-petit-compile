---
name: gerer-sources
description: Gère les sources de veille-auto dans config/sources.json - ajouter, retirer, tester ou réparer un flux RSS/Atom, trouver l'URL du flux d'un site, ajouter ou modifier une rubrique, régler window_hours ou max_per_feed. Utilise cette skill quand l'utilisateur veut suivre un nouveau site, quand collect.py signale ECHEC pour une source, ou quand il veut changer les rubriques de la revue de presse.
---

# Gérer les sources

Référence complète : [doc/sources.md](../../../doc/sources.md). Fonctionnement de la collecte : [doc/collecte.md](../../../doc/collecte.md).

## Ajouter un flux

1. **Trouver l'URL du flux.** Si l'utilisateur donne l'adresse du site :

   ```bash
   curl -sL -A "Mozilla/5.0" "https://exemple.org/" | grep -io '<link[^>]*\(rss\|atom\)[^>]*>'
   ```

   Sinon, essaie `/feed`, `/rss`, `/rss.xml`, `/atom.xml`, `/feed.xml`, `/index.xml`.
2. **Vérifier le flux.** La réponse doit être du XML avec des `<item>` ou `<entry>` datés :

   ```bash
   curl -sL -A "Mozilla/5.0" "<url>" | head -c 2000
   ```

3. **Choisir la rubrique.** Prends l'`id` dont le contenu correspond au sujet principal du site (table dans [doc/redaction.md](../../../doc/redaction.md)). Si le site couvre plusieurs sujets, demande à l'utilisateur.
4. **Ajouter l'entrée** dans `feeds`, sur le modèle des voisines : `{"name": "Nom usuel du média", "url": "…"}`. Place un flux d'origine avant un agrégateur : en cas de doublon, `collect.py` garde le premier flux.
5. **Tester.**

   ```bash
   python scripts/collect.py
   python -c "import json;[print(f) for f in json.load(open('work/candidates.json',encoding='utf-8'))['flux'] if f['name']=='Nom usuel du média']"
   ```

   `ok: true` et `count` supérieur à 0 : c'est bon. `count: 0` : relance avec `--hours 168` pour vérifier que le flux publie bien.
6. **Valider la config** : `python scripts/build.py --check`.

## Réparer un flux en échec

Lis l'erreur dans la sortie de `collect.py` (`ECHEC <nom>: <erreur>`) :

| Erreur | Action |
| --- | --- |
| `HTTP Error 404` | L'URL a changé. Cherche la nouvelle sur le site (étape 1 ci-dessus). |
| `HTTP Error 403` ou `429` | Le site bloque les robots. Cherche un autre flux du média ou propose de retirer la source. |
| `ParseError` | Le flux renvoie du HTML. Ouvre-le avec `curl` pour voir la réponse. |
| `timed out`, `URLError` sur une seule source | Relance plus tard ; si l'échec dure plusieurs jours, traite comme un 404. |

Avant de retirer une source, demande l'accord de l'utilisateur.

## Ajouter ou modifier une rubrique

- Nouvelle rubrique : `id` court, minuscules, sans accent ; `nom` affiché ; `couleur` hexadécimale lisible en clair et en sombre ; `cible` du type `"2 à 4"`. Place-la à la position voulue sur le site.
- Après l'ajout, mets à jour la liste des `id` à l'étape 5 de `ROUTINE.md`, la liste des rubriques du `README.md` et les tables de `doc/sources.md` et `doc/redaction.md`.
- Garde le total des `cible` entre 25 et 40, la fourchette de ROUTINE.md.
- **Ne renomme ni ne supprime un `id` utilisé par une édition** sans l'accord de l'utilisateur. Vérifie d'abord :

  ```bash
  grep -l '"rubrique": "<id>"' data/editions/*.json
  ```

  Changer `nom`, `couleur` ou `cible` est sans risque.

## Terminer

- Mets à jour la table « Rubriques actuelles » de [doc/sources.md](../../../doc/sources.md).
- `python scripts/build.py --check` doit passer.
- Propose un commit `feat(sources): ajoute <média>` ou `fix(sources): remplace le flux de <média>`. Ne commite pas `work/`.
