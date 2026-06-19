# Skill `coach-lol` — design

Date : 2026-06-19
Statut : design validé, en attente de relecture avant plan d'implémentation.

## But

Un skill Claude Code qui prend **un match ID** en entrée et produit un **débrief de coaching tranché**
sur une partie classée de l'utilisateur (Niir#EUW), puis permet un **drill-down** interactif.

Constat de départ : l'utilisateur a déjà un outil qui sort des stats brutes et « ça ne l'aide pas plus
que ça ». Ce skill doit faire l'inverse d'un mur de chiffres : isoler **2-3 fautes qui ont réellement
coûté la game**, démontrées par les données de la timeline.

Le skill est **à 90 % un problème d'accès à la donnée, 10 % de coaching** : le coaching est la partie
que le modèle sait déjà faire ; la valeur du skill est dans la plomberie de données fiable + la
hiérarchisation par impact réel.

## Périmètre

Dans le périmètre :
- Entrée = un match ID (région EUW par défaut).
- Source = API officielle Riot (clé **Personal** persistante ; une clé **dev** fonctionne à l'identique en attendant).
- Rapport auto structuré, puis drill-down (questions ciblées + analyse de screenshots collés).
- Une game à la fois.

Hors-scope volontaire (YAGNI) :
- Pas d'analyse mécanique pixel-par-pixel du replay (skillshots dodgés, spacing) — impossible sans CV vidéo.
- Pas de mode « live » / commentaire temps réel.
- Pas de base de données multi-games, pas de stockage persistant des parties.
- Pas de modèle local / GPU — l'intelligence est dans le modèle, la plomberie tourne sur la machine de l'utilisateur.

## Identité & accès

- **Riot ID** : `Niir#EUW` (gameName=`Niir`, tagLine=`EUW`). Stocké dans la config du skill pour le repérage automatique.
- **Routing** : EUW → plateforme `euw1`, cluster régional `europe.api.riotgames.com` pour `account-v1` et `match-v5`.
- **Clé API** : valeur stockée dans un fichier **local et gitignoré** (jamais commité, jamais affiché). Le skill la lit à l'exécution.

## Couche données

Chaîne d'appels :
1. `account-v1/accounts/by-riot-id/Niir/EUW` (cluster europe) → `puuid` de l'utilisateur.
2. `match-v5/matches/EUW1_<matchId>` → résumé complet du match (les 10 participants, stats, builds, runes, timestamps d'objectifs).
3. `match-v5/matches/EUW1_<matchId>/timeline` → frames toutes les ~60s : positions, or, niveau, achats d'items, wards posées/détruites, chaque kill horodaté avec position.
4. Repérage : trouver le participant dont le `puuid` == celui de l'utilisateur → c'est « toi » dans l'analyse.

Données de référence (benchmarks) : Data Dragon pour le mapping championId→nom ; benchmarks CS/vision par rôle
établis à partir de seuils connus (à figer dans le skill, pas d'appel externe supplémentaire).

Robustesse : gérer clé expirée/invalide (401/403), match introuvable (404), rate limit (429) avec messages clairs.

## Rapport auto

Sorti dès que l'utilisateur fournit un match ID. Sections, par ordre d'impact :

1. **Verdict en 1 ligne** — pourquoi cette game est perdue, sans détour.
2. **Contexte** — champ joué, rôle, matchup direct, résultat, durée.
3. **Phase de lane** — CS@10 / CS@14, diff d'or et d'XP vs adversaire de lane, premières morts, comparé au benchmark du rôle.
4. **Tes morts, une par une** (depuis la timeline) — chacune : minute, lieu (zone de la map), état d'or au moment, qui t'a tué, et la **lecture** : overextend ? sans vision ? mauvais timing / mauvais trade ?
5. **Tournants de la game** — à quelle minute le lead d'or d'équipe a basculé, autour de quel objectif (dragon/herald/baron/tour).
6. **Macro / vision** — participation aux objectifs (présence à leur prise), vision score vs benchmark du rôle.
7. **2-3 axes prioritaires** — tranchés, actionnables, hiérarchisés. Pas une liste de 10.

Principe : chaque affirmation est **adossée à une donnée** (minute, valeur, position). Pas d'analyse au doigt mouillé.

## Drill-down

Après le rapport, l'utilisateur enchaîne librement :
- *« explique ma mort à 14:30 »* → le skill ressort le contexte timeline de ce timestamp (positions des 10 joueurs, or, objectifs récents).
- *« c'était quoi l'état de map à ce moment »* → réponse depuis la timeline.
- L'utilisateur **colle un screenshot** d'un instant → le modèle lit la scène (vision) et la **croise avec la donnée timeline** du timestamp le plus proche.

## Ton

Franc, sans complaisance, hiérarchisé par impact réel (préférence explicite de l'utilisateur). Le but est la
progression, pas le réconfort.

## Découpage du skill (unités)

- **Config** : lecture Riot ID + clé (fichier local gitignoré). Une responsabilité : fournir identité + auth.
- **Client Riot** : enchaîne les 3 appels, gère erreurs/rate limit, renvoie match + timeline + puuid utilisateur. Testable en isolation.
- **Extraction/repérage** : localise le participant utilisateur, calcule les dérivés (CS@10, diffs, liste de morts annotées, tournants).
- **Génération du débrief** : transforme les dérivés en rapport structuré (instructions de coaching dans le skill).
- **Drill-down** : accès à la timeline par timestamp + fusion avec screenshots.

## Setup (one-time)

1. Mettre la clé API dans le fichier de config local gitignoré.
2. Confirmer/écrire le Riot ID `Niir#EUW` dans la config.
3. Vérifier que le `.gitignore` exclut bien le fichier de config.

## Démarrage / test

Première cible de test : la « pire game récente » de l'utilisateur, `7891869242` (→ `EUW1_7891869242`).
