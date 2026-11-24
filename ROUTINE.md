# Consignes de l'édition quotidienne

Ce fichier guide l'agent Claude qui produit l'édition chaque matin. Suis les étapes dans l'ordre. Ne modifie ni `scripts/`, ni `templates/`, ni `config/`, ni ce fichier.

## 1. Préparer

```bash
DATE=$(TZ=Europe/Paris date +%F)
ls data/editions/ 2>/dev/null | tail -3
```

Si `data/editions/$DATE.json` existe déjà, l'édition du jour est faite : arrête-toi et dis-le.

## 2. Collecter

```bash
python3 scripts/collect.py
```

Le script écrit `work/candidates.json`. Il contient :

- `flux` : l'état de chaque source (`ok`, `count`, `error`) ;
- `candidats` : les articles des 30 dernières heures, sans ceux déjà publiés. Chaque candidat a `rubrique_suggeree` (ou `null` pour la une de Hacker News), `source`, `titre`, `url`, `date`, `extrait` et `hn` (points et commentaires Hacker News, ou `null`).

Si moins de la moitié des sources répondent, réessaie une fois. Si l'échec continue, poursuis avec ce que tu as et signale-le à la fin.

## 3. Sélectionner

Lis tous les candidats, puis choisis :

- **1 article « à la une »** : le plus important du jour pour un développeur curieux de tech, d'IA et de jeu vidéo ;
- **25 à 40 articles** répartis dans les rubriques de `config/sources.json`. Le champ `cible` de chaque rubrique donne le nombre visé. Une rubrique sans bon article peut rester vide.

**Grandes actualités d'abord.** Avant d'appliquer le profil, compte les sources par sujet. Un sujet repris par au moins 3 sources différentes est une actualité majeure du jour (exemple : changement de PDG d'un géant de la tech, rachat géant, panne mondiale). Garde-le toujours, même hors profil, en un seul article dans la rubrique qui lui va. Il peut faire la une.

**Profil du lecteur.** DevOps orienté web et IA, qui aime bidouiller, surtout autour de l'IA. Applique ce profil aux autres choix : il sert à départager, pas à écarter l'actualité majeure.

- Favorise : LLM, agents, MCP, RAG, outils et modèles IA utilisables ; DevOps web (Docker, CI/CD, self-hosting, déploiement, observabilité) ; bidouille concrète ; recompilation ou décompilation de vieux jeux assistée par IA ; failles et incidents qui touchent le web, le cloud, les paquets ou les outils de dev.
- Écarte : failles de matériel exotique (routeurs, KVM, IoT) et exploitations trop techniques ou sans action possible pour le lecteur ; outils et tutos trop avancés (théorie, internes de noyau, calcul haute performance) ; notes de version Linux ou de distribution sans impact pour un dev web/IA.
- `linux` : peu d'articles. Ne garde que ce qui change l'usage d'un dev (outils, conteneurs, sécurité, noyau seulement si impact large). Une rubrique à 0 ou 1 article est acceptable.
- `retro` : garde aussi les projets de décompilation, recompilation ou portage de vieux jeux par IA.
- `tutos` : accessible et immédiatement utilisable, orienté IA, web et DevOps.

Règles de tri :

- Privilégie le neuf et le concret : sorties, versions, failles avec CVE, annonces, découvertes, outils utilisables.
- Écarte les bons plans, tests de produits sponsorisés, promotions, listes « top 10 », rumeurs sans source et articles sans rapport avec la tech, la science ou le jeu vidéo.
- Plusieurs sources sur le même sujet : garde un seul article, celui de la source la plus complète ou d'origine.
- `rubrique_suggeree` n'est qu'une indication : range chaque article dans la rubrique qui lui va vraiment. Les candidats Hacker News (`rubrique_suggeree: null`) vont dans la rubrique de leur sujet, ou sont écartés.
- `tutos` : tutoriels, guides et outils utilisables tout de suite (Show HN, bibliothèques, astuces de dev). Un candidat d'une autre rubrique peut y aller.
- `jeux` : jeux vidéo récents ou à venir. `retro` : rétro gaming, homebrew, émulation, matériel ancien.
- Un score HN élevé est un bon signal d'intérêt. Au-delà de 300 points, garde le sujet sauf s'il est sans rapport avec la tech ou relève des exclusions du profil. Au-delà de 200 points, préfère-le à un candidat sans score.

**Suivi des sujets.** Lis les titres des 14 dernières éditions de `data/editions/`. Si un article prolonge un sujet déjà traité, mets `"suite": true`. Ne republie pas une information déjà donnée sans fait nouveau.

## 4. Lire et rédiger

Pour l'article à la une, et pour chaque article dont l'extrait ne suffit pas, lis la page d'origine (`WebFetch`, ou `curl -sL` en dernier recours). Si la page est inaccessible, rédige à partir de l'extrait seul, sans rien inventer, ou écarte l'article.

Pour chaque article retenu, écris en français :

- `titre` : un titre informatif en français, qui dit ce qui se passe. Pas de clickbait, pas de point final. Garde les noms propres, numéros de version et CVE.
- `resume` : 2 à 4 phrases factuelles. Qui, quoi, chiffres clés, disponibilité. Uniquement des faits présents dans la source. Pour la une, 4 à 6 phrases.
- `pourquoi` : une phrase sur l'intérêt concret pour le lecteur (« à mettre à jour si… », « utile pour… », « change la donne pour… »). Pas de formule creuse.

N'invente jamais un chiffre, une date, une citation ou un nom. En cas de doute, ne l'écris pas.

## 5. Écrire l'édition

Crée `data/editions/$DATE.json`, encodé en UTF-8 :

```json
{
  "date": "AAAA-MM-JJ",
  "genere": "horodatage ISO 8601 de maintenant, ex. 2026-11-22T06:04:00+01:00",
  "une": { ...un article... },
  "items": [ { ...article... }, ... ]
}
```

Chaque article :

```json
{
  "rubrique": "secu",
  "source": "BleepingComputer",
  "titre": "…",
  "resume": "…",
  "pourquoi": "…",
  "url": "https://… (l'url du candidat)",
  "date": "date ISO du candidat, ou null",
  "suite": false,
  "hn": null
}
```

- `rubrique` : un `id` de `config/sources.json` (`secu`, `ia`, `dev`, `linux`, `decouvertes`, `jeux`, `retro`, `science`, `tutos`).
- `hn` : recopie l'objet `hn` du candidat s'il existe, sinon `null`.
- L'article à la une ne figure pas aussi dans `items`.
- Range `items` par rubrique, puis du plus important au moins important.

## 6. Valider

```bash
python3 scripts/build.py
```

Le script valide toutes les éditions et génère `docs/` (ignoré par git). S'il signale des erreurs, corrige le JSON et relance jusqu'à ce qu'il passe.

## 7. Publier

```bash
git add data/editions/$DATE.json
git commit -m "chore(edition): édition du $DATE"
git push origin HEAD:main || git push -u origin HEAD
```

Ne commite que le fichier de l'édition. Le workflow GitHub `publish.yml` fusionne une branche `claude/*` dans `main` si besoin, puis publie le site sur GitHub Pages.

## 8. Rendre compte

Termine par un message court : date et nombre d'articles par rubrique, titre de la une, sources en échec et problèmes rencontrés.
