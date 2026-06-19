---
name: coach-lol
description: Use when the user gives a League of Legends match ID and wants a coaching review of their game. Fetches the match via the Riot API and produces a blunt, prioritized debrief, then supports drill-down.
---

# Coach LoL

Review tranchée d'une partie de l'utilisateur (Niir#EUW) à partir d'un match ID.

## Étape 1 — Récupérer les faits

Lance le script depuis la racine du repo :

```bash
py .claude/skills/coach-lol/scripts/coach.py <matchId>
```

Il sort un JSON `{ match_info, lane, deaths, objectives, gold_timeline }`.
En cas d'`ERREUR:` (clé expirée, 404…), relaie le message tel quel et propose la correction.

## Étape 2 — Écrire le débrief auto

À partir du JSON, écris un débrief **en français, franc, hiérarchisé par impact réel** (l'utilisateur veut
du direct, pas du réconfort). Le script donne les chiffres ; **toi** tu fais le jugement. Sections, dans l'ordre :

1. **Verdict en 1 ligne** — pourquoi cette game est perdue.
2. **Contexte** — `match_info` (champ, rôle, matchup via `lane.opponent`, résultat, durée, KDA).
3. **Phase de lane** — compare `lane.cs_at` à `lane.cs_target`, commente `lane.gold_diff_at`. Sois concret (« -25 CS à 14 min, soit ~500 or de retard »).
4. **Tes morts** — pour chaque entrée de `deaths` : minute, zone, qui t'a tué. Déduis la lecture des faits :
   `allies_nearby == 0` + `zone` côté ennemi = overextend ; `enemies_nearby >= 2` = collapse subi.
   Ne dis jamais « sans vision » comme un fait — formule-le en hypothèse à vérifier (« sûrement sans vision sur le pixel — confirme ? »).
5. **Tournants** — repère dans `gold_timeline` la minute où `diff` bascule durablement, relie-la à un objectif (`objectives`).
6. **Macro / vision** — `objectives` (qui a pris quoi), `vision_score` vs `vision_target`.
7. **2-3 axes prioritaires** — tranchés, actionnables. Pas plus de 3.

## Étape 3 — Drill-down

Ensuite l'utilisateur enchaîne :
- « explique ma mort à 14:30 » → retrouve l'entrée `deaths` la plus proche, ressors le contexte (`gold_timeline` à cette minute, objectifs récents).
- L'utilisateur **colle un screenshot** → lis la scène et croise-la avec la donnée du timestamp le plus proche.

## Règles

- Chaque affirmation s'appuie sur une donnée (minute, valeur, zone). Pas d'analyse au doigt mouillé.
- Les benchmarks sont des **repères** (Plat+), pas une vérité absolue — dis-le si l'écart est marginal.
- Ne réaffiche jamais la clé API. Si le `.env` manque, renvoie vers le setup.
