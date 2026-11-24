# Architecture

## Principe

Le projet sépare le travail mécanique du travail éditorial :

- **Les scripts Python** font ce qui est déterministe : télécharger les flux, dédupliquer, valider le JSON, générer le HTML.
- **Claude** fait ce qui demande du jugement : choisir les articles, les lire, les ranger, rédiger en français.
- **GitHub Actions** publie : fusion éventuelle d'une branche `claude/*`, génération du site, déploiement sur GitHub Pages.

Le seul artefact versionné produit chaque jour est un fichier JSON : `data/editions/AAAA-MM-JJ.json`. Tout le reste (candidats, site HTML) est regénéré et ignoré par git.

## Arborescence

```text
le-petit-compile/
├── ROUTINE.md                  Consignes de la routine quotidienne (lues par Claude)
├── CLAUDE.md                   Contexte projet pour les sessions Claude Code
├── README.md                   Présentation courte
├── config/
│   └── sources.json            Rubriques, flux RSS, réglages globaux
├── scripts/
│   ├── collect.py              Collecte -> work/candidates.json
│   └── build.py                Validation + génération -> docs/
├── templates/
│   └── page.html               Gabarit unique de page (HTML, CSS, JS inline)
├── data/
│   └── editions/
│       └── AAAA-MM-JJ.json     Une édition par jour (versionnée)
├── doc/                        Cette documentation
├── .claude/skills/             Skills Claude Code du projet
├── .github/workflows/
│   ├── publish.yml             Fusion claude/* -> main, puis déploiement Pages
│   └── cleanup.yml             Suppression des branches claude/* déjà fusionnées
├── work/                       (ignoré) candidats de la collecte du jour
└── docs/                       (ignoré) site généré par build.py
```

> `docs/` est le dossier de sortie du site, pas la documentation. La documentation vit dans `doc/`.

## Flux de données

```text
config/sources.json ──┐
                      ├─► scripts/collect.py ──► work/candidates.json
data/editions/*.json ─┘        (déjà publiés ignorés)        │
                                                             ▼
                                              Claude (ROUTINE.md)
                                         sélection, lecture, rédaction
                                                             │
                                                             ▼
                                         data/editions/AAAA-MM-JJ.json
                                                             │
config/sources.json ──┐                                      │
templates/page.html ──┼─► scripts/build.py ◄─────────────────┘
                      │        (validation)
                      ▼
                docs/index.html + docs/editions/AAAA-MM-JJ.html
                      │
                      ▼
            git push ─► publish.yml ─► GitHub Pages
```

## Déroulé d'une journée

1. **05:00 UTC** : la routine Claude Code démarre dans le cloud, clone le dépôt et suit [ROUTINE.md](../ROUTINE.md).
2. Elle vérifie que l'édition du jour (date de Paris) n'existe pas déjà.
3. `python3 scripts/collect.py` télécharge en parallèle environ 33 flux RSS/Atom et la une de Hacker News, garde les articles des 30 dernières heures et retire les URL déjà publiées.
4. Claude lit les candidats, choisit une « une » et 25 à 40 articles, lit les pages d'origine si l'extrait ne suffit pas, et rédige titre, résumé et « pourquoi ».
5. Claude écrit `data/editions/AAAA-MM-JJ.json`, puis lance `python3 scripts/build.py` jusqu'à ce que la validation passe.
6. Claude commite uniquement ce fichier et pousse sur `main`, ou sur une branche `claude/*` si `main` lui est refusée.
7. `publish.yml` fusionne la branche si besoin, regénère le site et le déploie.
8. À 06:30 UTC, `cleanup.yml` supprime les branches `claude/*` déjà présentes dans `main`.

## Choix techniques

| Choix | Raison |
| --- | --- |
| Bibliothèque standard Python uniquement | La routine cloud tourne sans `pip install` ; rien ne casse à cause d'une dépendance. |
| JSON comme format d'édition | Facile à écrire pour Claude, facile à valider, diff lisible dans git. |
| Site regénéré entièrement à chaque build | Pas d'état caché : le site dépend seulement de `data/`, `config/` et `templates/`. |
| Données injectées dans la page (`<script type="application/json">`) | Une seule page par édition, aucun appel réseau côté lecteur sauf les polices. |
| Fuseau `Europe/Paris` pour la date | L'édition porte la date du lecteur français, même si la routine tourne en UTC. |
| Fusion des branches `claude/*` par Actions | La routine cloud peut n'avoir le droit de pousser que sur `claude/*`. |
