---
name: corriger-edition
description: Corrige une édition existante de veille-auto (data/editions/AAAA-MM-JJ.json) - erreurs de validation de scripts/build.py, JSON cassé, erreur factuelle, doublon, mauvaise rubrique, article à retirer ou à ajouter. Utilise cette skill quand build.py échoue, quand le workflow « Publier la veille » plante à « Générer le site », ou quand l'utilisateur signale un problème dans une édition publiée. Ne l'utilise pas pour créer une nouvelle édition (skill edition-du-jour).
---

# Corriger une édition

## 1. Diagnostiquer

```bash
python scripts/build.py --check
```

Chaque erreur indique le fichier et la position, par exemple `2026-11-22.json items[12] : rubrique inconnue « securite »`. La table des erreurs fréquentes est dans [doc/depannage.md](../../../doc/depannage.md), les règles complètes dans [doc/format-edition.md](../../../doc/format-edition.md).

Si `build.py` passe mais que l'utilisateur signale un problème de contenu, demande-lui quel article est en cause s'il ne l'a pas dit. Retrouve l'article par son titre ou son URL.

## 2. Corriger

Modifie le fichier avec l'outil Edit, article par article. Ne réécris pas le fichier entier.

| Problème | Correction |
| --- | --- |
| JSON invalide | Lis la ligne indiquée. Cause habituelle : guillemet droit non échappé dans un texte. Remplace-le par « » ou `\"`. |
| `date` différente du nom du fichier | Aligne `date` sur le nom du fichier, jamais l'inverse. |
| Rubrique inconnue | Remplace par un `id` de `config/sources.json`. |
| Champ manquant ou vide | Rédige-le à partir de la source. Si la source est inaccessible, retire l'article. |
| URL en double | Garde l'article le plus complet, retire l'autre. |
| Erreur factuelle | Ouvre la page d'origine (`url`) avec WebFetch. Corrige uniquement d'après la source. Si la source ne confirme rien, retire la phrase. |
| Mauvaise rubrique | Change `rubrique` et déplace l'article dans le bloc de sa nouvelle rubrique dans `items`. |
| Article à retirer | Supprime l'objet. Si c'est la une, promeus le meilleur article de `items` à la une et allonge son résumé à 4 à 6 phrases. |

Règles :

- Ne modifie jamais `url`, `source`, `date` ni `hn` d'un article, sauf si l'erreur porte sur ces champs.
- N'invente jamais un fait pour combler un champ.
- Ne touche qu'aux éditions concernées.

## 3. Une ancienne édition devient invalide après un changement de config

Si l'erreur vient d'un `id` de rubrique supprimé ou renommé dans `config/sources.json`, demande à l'utilisateur ce qu'il préfère :

- rétablir l'`id` dans la config (avec `"feeds": []` si la rubrique n'a plus de flux) ;
- ou migrer les éditions vers le nouvel `id`.

## 4. Valider et publier

1. `python scripts/build.py` doit passer sans erreur.
2. Montre le diff à l'utilisateur (`git diff data/editions/`).
3. Avec son accord, commite avec `fix(edition): <ce qui est corrigé> du AAAA-MM-JJ`, puis pousse. Le site se redéploie au push.
