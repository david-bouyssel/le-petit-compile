# Ligne éditoriale

Ce document explique les règles de [ROUTINE.md](../ROUTINE.md) et la façon de les appliquer. En cas de divergence, ROUTINE.md fait foi : c'est lui que la routine lit.

## Lecteur visé

Un développeur francophone curieux de tech, d'IA et de jeu vidéo. Il lit l'édition en quelques minutes le matin et veut savoir ce qui a changé, ce qui le concerne et ce qu'il doit faire.

## Volume

- 1 article à la une, plus 25 à 40 articles dans `items`.
- Chaque rubrique vise le nombre donné par son champ `cible` dans `config/sources.json`.
- Une rubrique sans bon article reste vide. Mieux vaut une rubrique vide qu'un article faible.

## Choisir la une

L'article le plus important du jour pour le lecteur visé. Signaux utiles :

- impact large : faille massivement exploitée, sortie majeure, décision qui touche beaucoup de développeurs ;
- nouveauté réelle et vérifiable ;
- forte discussion sur Hacker News (plusieurs centaines de points) ;
- couverture par plusieurs sources.

L'article de la une ne figure pas aussi dans `items`.

## Garder

- Sorties et nouvelles versions (avec numéro de version).
- Failles avec CVE, correctifs, attaques documentées.
- Annonces officielles, résultats publiés, découvertes scientifiques.
- Outils et bibliothèques utilisables tout de suite.
- Articles HN de plus de 200 points sur un sujet du périmètre.

## Écarter

- Bons plans, promotions, codes promo.
- Tests de produits sponsorisés, guides d'achat.
- Listes « top 10 », comparatifs génériques.
- Rumeurs sans source identifiée.
- Sujets hors tech, science et jeu vidéo.
- Informations déjà publiées sans fait nouveau.

## Doublons et suivi

- Plusieurs sources sur le même sujet : garde un seul article, celui de la source d'origine ou la plus complète.
- Lis les titres des 14 dernières éditions. Un article qui prolonge un sujet déjà traité reçoit `"suite": true` et doit apporter un fait nouveau.
- `collect.py` retire déjà les URL publiées, mais pas les mêmes sujets publiés sous une autre URL : c'est à toi de les repérer.

## Ranger dans les rubriques

`rubrique_suggeree` n'est qu'une indication tirée du flux d'origine. Range chaque article selon son sujet réel :

| Rubrique | Contenu |
| --- | --- |
| `secu` | Failles, attaques, fuites, correctifs, alertes CERT |
| `ia` | Modèles, outils IA, recherche, régulation de l'IA |
| `dev` | Langages, frameworks, pratiques, écosystème des développeurs |
| `linux` | Distributions, noyau, logiciels libres, gouvernance open source |
| `decouvertes` | Matériel, produits tech, industrie, usages numériques |
| `jeux` | Jeux vidéo récents ou à venir, industrie du jeu |
| `retro` | Rétro gaming, homebrew, émulation, matériel ancien |
| `science` | Sciences, espace, santé, climat |
| `tutos` | Tutoriels, guides, outils prêts à l'emploi, Show HN |

Les candidats HN (`rubrique_suggeree: null`) vont dans la rubrique de leur sujet, ou sont écartés.

## Rédiger

### `titre`

- En français, informatif : il dit ce qui se passe.
- Garde les noms propres, numéros de version et identifiants CVE.
- Pas de clickbait, pas de question, pas de point final.

| À éviter | À préférer |
| --- | --- |
| Cette faille va vous faire peur | Une faille de Fortinet FortiOS (CVE-2026-1234) exploitée avant le correctif |
| Linux 6.18 est là ! | Linux 6.18 sort avec le support de… |

### `resume`

- 2 à 4 phrases ; 4 à 6 pour la une.
- Qui, quoi, chiffres clés, disponibilité.
- Uniquement des faits présents dans la source.
- Attribue les affirmations non vérifiées : « selon Dragos », « d'après l'éditeur ».

### `pourquoi`

- Une phrase sur l'intérêt concret : « à mettre à jour si… », « utile pour… », « change la donne pour… ».
- Pas de formule creuse comme « une nouvelle à suivre de près ».

### Exactitude

- N'invente jamais un chiffre, une date, une citation ou un nom.
- En cas de doute, ne l'écris pas.
- Si l'extrait est trop court, lis la page d'origine. Si la page est inaccessible, rédige à partir de l'extrait seul ou écarte l'article.
- Garde l'`url` du candidat telle quelle.

## Ordre des `items`

Range les `items` par rubrique, dans l'ordre de `config/sources.json`, puis du plus important au moins important dans chaque rubrique. La page regroupe de toute façon les articles par rubrique, mais l'ordre interne est conservé.
