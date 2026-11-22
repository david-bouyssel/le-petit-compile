---
name: edition-du-jour
description: Produit l'édition quotidienne de la revue de presse « Le Petit Compilé » dans veille-auto - collecte des flux RSS, sélection, rédaction en français, validation et publication de data/editions/AAAA-MM-JJ.json. Utilise cette skill quand l'utilisateur demande de faire, générer, rattraper ou relancer l'édition du jour (ou d'une date manquée) hors de la routine cloud. Ne l'utilise pas pour corriger une édition existante (skill corriger-edition) ni pour modifier les sources (skill gerer-sources).
---

# Édition du jour

[ROUTINE.md](../../../ROUTINE.md) est la source de vérité. Lis-le en entier avant de commencer et suis ses 8 étapes dans l'ordre. Cette skill ajoute seulement ce qui change quand tu travailles en session locale plutôt que dans la routine cloud.

## Avant de commencer

1. Détermine la date de l'édition dans le fuseau `Europe/Paris` :

   ```bash
   TZ=Europe/Paris date +%F
   ```

   Sous Windows PowerShell : `[System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTime]::UtcNow, 'Romance Standard Time').ToString('yyyy-MM-dd')`.
2. Si `data/editions/<date>.json` existe déjà, arrête-toi et dis-le. Pour la modifier, utilise la skill `corriger-edition`.
3. Vérifie que l'arbre git est propre (`git status`). Si des fichiers sont modifiés, demande à l'utilisateur avant de continuer.
4. Utilise `python` si `python3` n'existe pas (Windows).

## Rattraper une date manquée

Si l'utilisateur demande une édition pour une date passée :

- Lance la collecte avec une fenêtre qui couvre cette date, par exemple `python scripts/collect.py --hours 54` pour la veille.
- Ne garde que les candidats publiés dans les 30 heures qui précèdent 06:00 (Paris) de la date visée.
- Nomme le fichier et le champ `date` avec la date visée. Mets l'heure réelle de rédaction dans `genere`.

## Pendant la rédaction

- Lis [doc/redaction.md](../../../doc/redaction.md) pour les critères de sélection et des exemples de titres.
- Le schéma exact et les règles de validation sont dans [doc/format-edition.md](../../../doc/format-edition.md).
- Écris le JSON avec l'outil Write, en UTF-8. Dans les textes, utilise les guillemets français « » plutôt que des guillemets droits, pour éviter les erreurs d'échappement.
- Garde chaque `url` et chaque objet `hn` exactement comme dans `work/candidates.json`.

## Avant de publier

1. `python scripts/build.py` doit afficher `N édition(s) valide(s)` sans erreur.
2. Relis la une et 5 articles au hasard : chaque fait doit figurer dans l'extrait ou la page lue.
3. Vérifie que l'article de la une n'est pas aussi dans `items`.
4. Demande à l'utilisateur la permission de commiter et de pousser. En session locale, ne pousse pas sans accord explicite.
5. Commite seulement `data/editions/<date>.json`, avec le message `chore(edition): édition du <date>`.

## Compte rendu

Termine comme l'étape 8 de ROUTINE.md : date, nombre d'articles par rubrique, titre de la une, sources en échec, problèmes rencontrés.
