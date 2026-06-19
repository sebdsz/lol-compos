# Skill `coach-lol` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Un skill Claude Code qui prend un match ID, récupère la game de l'utilisateur (Niir#EUW) via l'API Riot, en extrait des faits exploitables, puis produit un débrief de coaching tranché suivi d'un drill-down interactif.

**Architecture:** Un script Python (stdlib uniquement) fait la plomberie réseau (Riot ID → puuid → match → timeline) et le calcul déterministe (CS@10/14, morts annotées, tournants, objectifs), et sort **un seul JSON de faits**. Le `SKILL.md` instruit le modèle à lancer ce script puis à écrire le débrief à partir des faits — le script ne juge jamais, il fournit les chiffres ; le modèle interprète.

**Tech Stack:** Python 3.12 (stdlib `urllib`, `json`, `os`), pytest pour les tests (un seul `pip install`), API Riot match-v5 + account-v1, cluster `europe.api.riotgames.com`.

---

## File Structure

```
D:/LoL/.claude/skills/coach-lol/
  SKILL.md                      # frontmatter + instructions (lancer le script, écrire le débrief, drill-down)
  scripts/
    config.py                   # lit .env (RIOT_API_KEY) + Riot ID -> identité/auth
    riot_client.py              # appels API: get_puuid, get_match, get_timeline (+ mapping erreurs)
    benchmarks.py               # seuils CS/vision par rôle (repères Plat+, codés en dur)
    analyze.py                  # fonctions pures: participant, lane, morts, tournants, objectifs
    coach.py                    # CLI orchestrateur: config -> client -> analyze -> JSON stdout
  tests/
    fixtures/
      sample_match.json         # match-v5 minimal mais conforme au schéma
      sample_timeline.json      # timeline-v5 minimale mais conforme au schéma
    test_analyze.py             # TDD des fonctions pures contre les fixtures
    test_client.py              # test du mapping d'erreurs / construction d'URL (sans réseau)
```

Le `.env` est à la racine `D:/LoL/.env` (déjà créé, déjà gitignoré). Le script remonte d'`scripts/` jusqu'à trouver `.env`.

Responsabilités : `config` = identité+auth ; `riot_client` = I/O réseau ; `benchmarks` = repères ; `analyze` = calcul pur (le cœur testé) ; `coach` = glue/CLI ; `SKILL.md` = comportement du modèle.

---

## Task 1: Scaffold + config loader

**Files:**
- Create: `D:/LoL/.claude/skills/coach-lol/scripts/config.py`
- Create: `D:/LoL/.claude/skills/coach-lol/tests/test_config.py`

- [ ] **Step 1: Installer pytest (one-time)**

Run: `py -m pip install pytest`
Expected: `Successfully installed pytest-...` (ou « already satisfied »).

- [ ] **Step 2: Écrire le test qui échoue**

`D:/LoL/.claude/skills/coach-lol/tests/test_config.py`
```python
import os
import sys
import textwrap
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import config  # noqa: E402


def test_load_env_reads_key(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("RIOT_API_KEY=RGAPI-test-123\n", encoding="utf-8")
    monkeypatch.setattr(config, "find_env_file", lambda: str(env))
    assert config.load_api_key() == "RGAPI-test-123"


def test_load_env_missing_key_raises(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("OTHER=x\n", encoding="utf-8")
    monkeypatch.setattr(config, "find_env_file", lambda: str(env))
    with pytest.raises(config.ConfigError):
        config.load_api_key()


def test_riot_id_default():
    assert config.RIOT_ID == ("Niir", "EUW")
```

- [ ] **Step 3: Lancer le test, vérifier l'échec**

Run: `py -m pytest D:/LoL/.claude/skills/coach-lol/tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'config'`.

- [ ] **Step 4: Écrire l'implémentation minimale**

`D:/LoL/.claude/skills/coach-lol/scripts/config.py`
```python
"""Identité + auth pour le skill coach-lol. Aucune valeur secrète n'est codée en dur."""
import os

# Riot ID de l'utilisateur (gameName, tagLine). Modifiable si le compte change.
RIOT_ID = ("Niir", "EUW")

# Région : EUW -> plateforme euw1, cluster régional europe.
PLATFORM = "euw1"
REGION_CLUSTER = "europe"


class ConfigError(Exception):
    pass


def find_env_file():
    """Remonte l'arborescence depuis ce fichier jusqu'à trouver un .env."""
    d = os.path.dirname(os.path.abspath(__file__))
    while True:
        candidate = os.path.join(d, ".env")
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(d)
        if parent == d:
            raise ConfigError("Aucun fichier .env trouvé en remontant l'arborescence.")
        d = parent


def load_api_key():
    path = find_env_file()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("RIOT_API_KEY="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    return value
    raise ConfigError("RIOT_API_KEY introuvable ou vide dans le .env.")
```

- [ ] **Step 5: Lancer le test, vérifier le succès**

Run: `py -m pytest D:/LoL/.claude/skills/coach-lol/tests/test_config.py -v`
Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/coach-lol/scripts/config.py .claude/skills/coach-lol/tests/test_config.py
git commit -m "feat(coach-lol): config loader (.env + Riot ID)"
```

---

## Task 2: Client Riot (réseau) + mapping d'erreurs

**Files:**
- Create: `D:/LoL/.claude/skills/coach-lol/scripts/riot_client.py`
- Create: `D:/LoL/.claude/skills/coach-lol/tests/test_client.py`

- [ ] **Step 1: Écrire le test qui échoue (URL + erreurs, sans réseau)**

`D:/LoL/.claude/skills/coach-lol/tests/test_client.py`
```python
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import riot_client  # noqa: E402


def test_match_full_id_builds_region_prefix():
    assert riot_client.full_match_id("7891869242") == "EUW1_7891869242"
    # déjà préfixé : inchangé
    assert riot_client.full_match_id("EUW1_7891869242") == "EUW1_7891869242"


def test_map_http_error_messages():
    assert "clé" in riot_client.explain_status(401).lower()
    assert "clé" in riot_client.explain_status(403).lower()
    assert "introuvable" in riot_client.explain_status(404).lower()
    assert "rate limit" in riot_client.explain_status(429).lower()


def test_account_url():
    url = riot_client.account_url("Niir", "EUW")
    assert "europe.api.riotgames.com" in url
    assert "/riot/account/v1/accounts/by-riot-id/Niir/EUW" in url
```

- [ ] **Step 2: Lancer le test, vérifier l'échec**

Run: `py -m pytest D:/LoL/.claude/skills/coach-lol/tests/test_client.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'riot_client'`.

- [ ] **Step 3: Écrire l'implémentation**

`D:/LoL/.claude/skills/coach-lol/scripts/riot_client.py`
```python
"""Client API Riot minimal (stdlib). I/O réseau isolée ici."""
import json
import urllib.request
import urllib.parse
import urllib.error

import config

_CLUSTER = f"https://{config.REGION_CLUSTER}.api.riotgames.com"


class RiotError(Exception):
    pass


def explain_status(status):
    return {
        401: "Clé API invalide ou absente (401). Vérifie RIOT_API_KEY dans le .env.",
        403: "Clé API refusée ou expirée (403). Une clé dev expire toutes les 24h — régénère-la.",
        404: "Ressource introuvable (404). Match ID ou Riot ID incorrect ?",
        429: "Rate limit atteint (429). Attends quelques secondes et réessaie.",
    }.get(status, f"Erreur HTTP {status}.")


def full_match_id(match_id):
    if "_" in match_id:
        return match_id
    return f"{config.PLATFORM.upper()}_{match_id}"


def account_url(game_name, tag_line):
    g = urllib.parse.quote(game_name)
    t = urllib.parse.quote(tag_line)
    return f"{_CLUSTER}/riot/account/v1/accounts/by-riot-id/{g}/{t}"


def _get(url, api_key):
    req = urllib.request.Request(url, headers={"X-Riot-Token": api_key})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RiotError(explain_status(e.code)) from e
    except urllib.error.URLError as e:
        raise RiotError(f"Problème réseau: {e.reason}") from e


def get_puuid(api_key, game_name, tag_line):
    return _get(account_url(game_name, tag_line), api_key)["puuid"]


def get_match(api_key, match_id):
    mid = full_match_id(match_id)
    return _get(f"{_CLUSTER}/lol/match/v5/matches/{mid}", api_key)


def get_timeline(api_key, match_id):
    mid = full_match_id(match_id)
    return _get(f"{_CLUSTER}/lol/match/v5/matches/{mid}/timeline", api_key)
```

- [ ] **Step 4: Lancer le test, vérifier le succès**

Run: `py -m pytest D:/LoL/.claude/skills/coach-lol/tests/test_client.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/coach-lol/scripts/riot_client.py .claude/skills/coach-lol/tests/test_client.py
git commit -m "feat(coach-lol): client Riot (account/match/timeline) + mapping erreurs"
```

---

## Task 3: Benchmarks + fixtures de test

**Files:**
- Create: `D:/LoL/.claude/skills/coach-lol/scripts/benchmarks.py`
- Create: `D:/LoL/.claude/skills/coach-lol/tests/fixtures/sample_match.json`
- Create: `D:/LoL/.claude/skills/coach-lol/tests/fixtures/sample_timeline.json`

- [ ] **Step 1: Écrire les benchmarks (repères Plat+, codés en dur)**

`D:/LoL/.claude/skills/coach-lol/scripts/benchmarks.py`
```python
"""Repères Plat+ par rôle. Ce sont des indicateurs, pas une vérité absolue."""

# CS attendu (minions + monstres) à 10 et 14 min, par teamPosition.
CS_AT = {
    "TOP":     {10: 72, 14: 105},
    "MIDDLE":  {10: 78, 14: 115},
    "BOTTOM":  {10: 80, 14: 118},
    "JUNGLE":  {10: 68, 14: 98},
    "UTILITY": {10: 18, 14: 28},
}

# Vision score attendu en fin de game (~30 min), par rôle.
VISION_AT_30 = {
    "TOP": 20, "MIDDLE": 24, "BOTTOM": 22, "JUNGLE": 30, "UTILITY": 50,
}


def cs_target(position, minute):
    return CS_AT.get(position, CS_AT["MIDDLE"]).get(minute)


def vision_target(position, game_minutes):
    base = VISION_AT_30.get(position, 24)
    if not game_minutes:
        return base
    return round(base * game_minutes / 30.0)
```

- [ ] **Step 2: Écrire la fixture match (schéma match-v5 minimal, 2 joueurs utiles)**

`D:/LoL/.claude/skills/coach-lol/tests/fixtures/sample_match.json`
```json
{
  "metadata": { "participants": ["PUUID_ME", "PUUID_ENEMY"] },
  "info": {
    "gameDuration": 1500,
    "participants": [
      { "puuid": "PUUID_ME", "participantId": 1, "teamId": 100, "championName": "LeBlanc",
        "teamPosition": "MIDDLE", "win": false, "kills": 4, "deaths": 7, "assists": 3,
        "totalMinionsKilled": 150, "neutralMinionsKilled": 5, "visionScore": 14,
        "goldEarned": 9000 },
      { "puuid": "PUUID_ENEMY", "participantId": 6, "teamId": 200, "championName": "Ahri",
        "teamPosition": "MIDDLE", "win": true, "kills": 9, "deaths": 2, "assists": 6,
        "totalMinionsKilled": 200, "neutralMinionsKilled": 0, "visionScore": 28,
        "goldEarned": 13000 }
    ]
  }
}
```

- [ ] **Step 3: Écrire la fixture timeline (frames à 10 et 14 min + un kill)**

`D:/LoL/.claude/skills/coach-lol/tests/fixtures/sample_timeline.json`
```json
{
  "info": {
    "frames": [
      { "timestamp": 600000,
        "participantFrames": {
          "1": { "participantId": 1, "minionsKilled": 55, "jungleMinionsKilled": 0,
                 "totalGold": 3500, "xp": 5000, "level": 8, "position": { "x": 7000, "y": 7400 } },
          "6": { "participantId": 6, "minionsKilled": 70, "jungleMinionsKilled": 0,
                 "totalGold": 4200, "xp": 5600, "level": 9, "position": { "x": 8000, "y": 8000 } }
        },
        "events": [] },
      { "timestamp": 840000,
        "participantFrames": {
          "1": { "participantId": 1, "minionsKilled": 80, "jungleMinionsKilled": 0,
                 "totalGold": 5000, "xp": 7500, "level": 10, "position": { "x": 11000, "y": 11000 } },
          "6": { "participantId": 6, "minionsKilled": 110, "jungleMinionsKilled": 0,
                 "totalGold": 7000, "xp": 8800, "level": 12, "position": { "x": 12200, "y": 9100 } }
        },
        "events": [
          { "type": "CHAMPION_KILL", "timestamp": 800000, "killerId": 6, "victimId": 1,
            "assistingParticipantIds": [], "position": { "x": 12000, "y": 9000 } },
          { "type": "ELITE_MONSTER_KILL", "timestamp": 820000, "killerTeamId": 200,
            "monsterType": "DRAGON" }
        ] }
    ]
  }
}
```

- [ ] **Step 4: Vérifier que les JSON sont valides**

Run: `py -c "import json; json.load(open(r'D:/LoL/.claude/skills/coach-lol/tests/fixtures/sample_match.json')); json.load(open(r'D:/LoL/.claude/skills/coach-lol/tests/fixtures/sample_timeline.json')); print('JSON OK')"`
Expected: `JSON OK`.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/coach-lol/scripts/benchmarks.py .claude/skills/coach-lol/tests/fixtures/
git commit -m "feat(coach-lol): benchmarks par rôle + fixtures de test"
```

---

## Task 4: Analyze — participant + phase de lane

**Files:**
- Create: `D:/LoL/.claude/skills/coach-lol/scripts/analyze.py`
- Create: `D:/LoL/.claude/skills/coach-lol/tests/test_analyze.py`

- [ ] **Step 1: Écrire le test qui échoue**

`D:/LoL/.claude/skills/coach-lol/tests/test_analyze.py`
```python
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import analyze  # noqa: E402

FIX = os.path.join(os.path.dirname(__file__), "fixtures")
MATCH = json.load(open(os.path.join(FIX, "sample_match.json"), encoding="utf-8"))
TL = json.load(open(os.path.join(FIX, "sample_timeline.json"), encoding="utf-8"))


def test_find_participant():
    p = analyze.find_participant(MATCH, "PUUID_ME")
    assert p["participantId"] == 1
    assert p["championName"] == "LeBlanc"


def test_lane_stats_cs_and_diff():
    me = analyze.find_participant(MATCH, "PUUID_ME")
    lane = analyze.lane_stats(MATCH, TL, me)
    assert lane["cs_at"][10] == 55          # 55 minions + 0 jungle
    assert lane["cs_at"][14] == 80
    assert lane["cs_target"][10] == 78      # benchmark MIDDLE
    assert lane["gold_diff_at"][14] == -2000  # 5000 - 7000 vs adversaire de lane
```

- [ ] **Step 2: Lancer le test, vérifier l'échec**

Run: `py -m pytest D:/LoL/.claude/skills/coach-lol/tests/test_analyze.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'analyze'`.

- [ ] **Step 3: Écrire l'implémentation**

`D:/LoL/.claude/skills/coach-lol/scripts/analyze.py`
```python
"""Calcul pur sur match-v5 + timeline-v5. Renvoie des FAITS, jamais de jugement."""
import benchmarks


def find_participant(match, puuid):
    for p in match["info"]["participants"]:
        if p["puuid"] == puuid:
            return p
    raise ValueError(f"puuid {puuid} absent du match.")


def _lane_opponent(match, me):
    """Adversaire direct = même teamPosition, équipe opposée."""
    for p in match["info"]["participants"]:
        if p["teamId"] != me["teamId"] and p.get("teamPosition") == me.get("teamPosition"):
            return p
    return None


def _frame_at(timeline, minute):
    target_ms = minute * 60000
    best = None
    for f in timeline["info"]["frames"]:
        if f["timestamp"] <= target_ms + 1:
            best = f
    return best


def _pframe(frame, pid):
    return frame["participantFrames"][str(pid)]


def _cs(pframe):
    return pframe.get("minionsKilled", 0) + pframe.get("jungleMinionsKilled", 0)


def lane_stats(match, timeline, me):
    opp = _lane_opponent(match, me)
    pos = me.get("teamPosition", "MIDDLE")
    cs_at, cs_target, gold_diff = {}, {}, {}
    for minute in (10, 14):
        frame = _frame_at(timeline, minute)
        if frame is None:
            continue
        mf = _pframe(frame, me["participantId"])
        cs_at[minute] = _cs(mf)
        cs_target[minute] = benchmarks.cs_target(pos, minute)
        if opp is not None:
            of = _pframe(frame, opp["participantId"])
            gold_diff[minute] = mf["totalGold"] - of["totalGold"]
    return {
        "position": pos,
        "opponent": opp["championName"] if opp else None,
        "cs_at": cs_at,
        "cs_target": cs_target,
        "gold_diff_at": gold_diff,
    }
```

- [ ] **Step 4: Lancer le test, vérifier le succès**

Run: `py -m pytest D:/LoL/.claude/skills/coach-lol/tests/test_analyze.py -v`
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/coach-lol/scripts/analyze.py .claude/skills/coach-lol/tests/test_analyze.py
git commit -m "feat(coach-lol): analyze participant + phase de lane"
```

---

## Task 5: Analyze — morts annotées

**Files:**
- Modify: `D:/LoL/.claude/skills/coach-lol/scripts/analyze.py`
- Modify: `D:/LoL/.claude/skills/coach-lol/tests/test_analyze.py`

- [ ] **Step 1: Ajouter le test qui échoue**

Ajouter à la fin de `tests/test_analyze.py` :
```python
def test_annotate_deaths():
    me = analyze.find_participant(MATCH, "PUUID_ME")
    deaths = analyze.annotate_deaths(MATCH, TL, me)
    assert len(deaths) == 1
    d = deaths[0]
    assert d["minute"] == 13              # 800000 ms -> 13 min
    assert d["zone"] == "jungle_ennemi"   # x/y ~ 12000,9000 : hors-diagonale, moitié ennemie
    assert d["killer"] == "Ahri"
    assert d["my_gold"] == 5000           # frame la plus proche
    assert d["allies_nearby"] == 0
    assert d["enemies_nearby"] >= 1
```

- [ ] **Step 2: Lancer le test, vérifier l'échec**

Run: `py -m pytest D:/LoL/.claude/skills/coach-lol/tests/test_analyze.py::test_annotate_deaths -v`
Expected: FAIL — `AttributeError: module 'analyze' has no attribute 'annotate_deaths'`.

- [ ] **Step 3: Implémenter (ajouter à `analyze.py`)**

Ajouter à la fin de `scripts/analyze.py` :
```python
def _zone(x, y):
    """Zone grossière sur la map (0..15000). Repère pour lire l'overextend, pas une science exacte.

    - moitié de map : la diagonale bot-gauche(0,0) -> top-droite(15000,15000) sépare allié/ennemi.
    - proche de cette diagonale = axe mid ; sinon = jungle/side.
    """
    if x is None or y is None:
        return "inconnue"
    side = "ennemi" if (x + y) > 15000 else "allie"
    place = "mid" if abs(x - y) < 2200 else "jungle"
    return f"{place}_{side}"


def _id_to_champ(match):
    return {p["participantId"]: p["championName"] for p in match["info"]["participants"]}


def _nearest_frame(timeline, ts_ms):
    best = timeline["info"]["frames"][0]
    for f in timeline["info"]["frames"]:
        if abs(f["timestamp"] - ts_ms) < abs(best["timestamp"] - ts_ms):
            best = f
    return best


def _dist(a, b):
    return ((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2) ** 0.5


def annotate_deaths(match, timeline, me):
    champ = _id_to_champ(match)
    my_id = me["participantId"]
    my_team = me["teamId"]
    team_of = {p["participantId"]: p["teamId"] for p in match["info"]["participants"]}
    deaths = []
    for frame in timeline["info"]["frames"]:
        for ev in frame.get("events", []):
            if ev.get("type") != "CHAMPION_KILL" or ev.get("victimId") != my_id:
                continue
            ts = ev["timestamp"]
            pos = ev.get("position", {})
            near = _nearest_frame(timeline, ts)
            mf = near["participantFrames"].get(str(my_id), {})
            allies = enemies = 0
            for pid_str, pf in near["participantFrames"].items():
                pid = int(pid_str)
                if pid == my_id:
                    continue
                if _dist(pf["position"], pos) <= 2000:
                    if team_of[pid] == my_team:
                        allies += 1
                    else:
                        enemies += 1
            deaths.append({
                "minute": ts // 60000,
                "timestamp_ms": ts,
                "zone": _zone(pos.get("x"), pos.get("y")),
                "position": pos,
                "killer": champ.get(ev.get("killerId"), "inconnu"),
                "assisters": len(ev.get("assistingParticipantIds", [])),
                "my_gold": mf.get("totalGold"),
                "allies_nearby": allies,
                "enemies_nearby": enemies,
            })
    return deaths
```

- [ ] **Step 4: Lancer tous les tests analyze, vérifier le succès**

Run: `py -m pytest D:/LoL/.claude/skills/coach-lol/tests/test_analyze.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/coach-lol/scripts/analyze.py .claude/skills/coach-lol/tests/test_analyze.py
git commit -m "feat(coach-lol): morts annotées (zone, or, alliés/ennemis proches)"
```

---

## Task 6: Analyze — tournants + objectifs/vision

**Files:**
- Modify: `D:/LoL/.claude/skills/coach-lol/scripts/analyze.py`
- Modify: `D:/LoL/.claude/skills/coach-lol/tests/test_analyze.py`

- [ ] **Step 1: Ajouter les tests qui échouent**

Ajouter à la fin de `tests/test_analyze.py` :
```python
def test_objectives_and_vision():
    me = analyze.find_participant(MATCH, "PUUID_ME")
    obj = analyze.objectives_and_vision(MATCH, TL, me)
    assert obj["my_team_objectives"]["DRAGON"] == 0   # dragon pris par l'équipe 200
    assert obj["enemy_objectives"]["DRAGON"] == 1
    assert obj["vision_score"] == 14
    assert obj["vision_target"] > 0


def test_gold_lead_timeline():
    me = analyze.find_participant(MATCH, "PUUID_ME")
    series = analyze.team_gold_timeline(MATCH, TL, me)
    # à 10 et 14 min mon équipe est derrière (or perso < adversaire ici)
    assert series[-1]["my_team_gold"] < series[-1]["enemy_team_gold"]
```

- [ ] **Step 2: Lancer, vérifier l'échec**

Run: `py -m pytest D:/LoL/.claude/skills/coach-lol/tests/test_analyze.py -k "objectives or gold_lead" -v`
Expected: FAIL — attributs `objectives_and_vision` / `team_gold_timeline` inexistants.

- [ ] **Step 3: Implémenter (ajouter à `analyze.py`)**

Ajouter à la fin de `scripts/analyze.py` :
```python
_ELITE = ("DRAGON", "RIFTHERALD", "BARON_NASHOR")


def objectives_and_vision(match, timeline, me):
    my_team = me["teamId"]
    mine = {k: 0 for k in _ELITE}
    enemy = {k: 0 for k in _ELITE}
    for frame in timeline["info"]["frames"]:
        for ev in frame.get("events", []):
            if ev.get("type") == "ELITE_MONSTER_KILL":
                mtype = ev.get("monsterType")
                if mtype not in mine:
                    continue
                if ev.get("killerTeamId") == my_team:
                    mine[mtype] += 1
                else:
                    enemy[mtype] += 1
    minutes = match["info"]["gameDuration"] / 60.0
    return {
        "my_team_objectives": mine,
        "enemy_objectives": enemy,
        "vision_score": me.get("visionScore"),
        "vision_target": benchmarks.vision_target(me.get("teamPosition", "MIDDLE"), minutes),
    }


def team_gold_timeline(match, timeline, me):
    my_team = me["teamId"]
    team_of = {p["participantId"]: p["teamId"] for p in match["info"]["participants"]}
    series = []
    for frame in timeline["info"]["frames"]:
        mine = enemy = 0
        for pid_str, pf in frame["participantFrames"].items():
            g = pf.get("totalGold", 0)
            if team_of[int(pid_str)] == my_team:
                mine += g
            else:
                enemy += g
        series.append({
            "minute": frame["timestamp"] // 60000,
            "my_team_gold": mine,
            "enemy_team_gold": enemy,
            "diff": mine - enemy,
        })
    return series
```

- [ ] **Step 4: Lancer tous les tests, vérifier le succès**

Run: `py -m pytest D:/LoL/.claude/skills/coach-lol/tests/ -v`
Expected: tous passed (config + client + analyze).

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/coach-lol/scripts/analyze.py .claude/skills/coach-lol/tests/test_analyze.py
git commit -m "feat(coach-lol): objectifs/vision + timeline d'or d'équipe"
```

---

## Task 7: CLI orchestrateur `coach.py`

**Files:**
- Create: `D:/LoL/.claude/skills/coach-lol/scripts/coach.py`

- [ ] **Step 1: Écrire l'orchestrateur**

`D:/LoL/.claude/skills/coach-lol/scripts/coach.py`
```python
"""CLI: python coach.py <matchId> -> JSON de faits sur stdout.

Usage:
    py coach.py 7891869242
Sortie: un objet JSON { match_info, lane, deaths, objectives, gold_timeline }.
"""
import json
import sys

import config
import riot_client
import analyze


def build_facts(match_id):
    api_key = config.load_api_key()
    game_name, tag_line = config.RIOT_ID
    puuid = riot_client.get_puuid(api_key, game_name, tag_line)
    match = riot_client.get_match(api_key, match_id)
    timeline = riot_client.get_timeline(api_key, match_id)
    me = analyze.find_participant(match, puuid)

    return {
        "match_info": {
            "match_id": riot_client.full_match_id(match_id),
            "champion": me["championName"],
            "position": me.get("teamPosition"),
            "win": me["win"],
            "duration_min": round(match["info"]["gameDuration"] / 60.0, 1),
            "kda": f'{me["kills"]}/{me["deaths"]}/{me["assists"]}',
        },
        "lane": analyze.lane_stats(match, timeline, me),
        "deaths": analyze.annotate_deaths(match, timeline, me),
        "objectives": analyze.objectives_and_vision(match, timeline, me),
        "gold_timeline": analyze.team_gold_timeline(match, timeline, me),
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: py coach.py <matchId>", file=sys.stderr)
        sys.exit(2)
    try:
        facts = build_facts(sys.argv[1])
    except (riot_client.RiotError, config.ConfigError, ValueError) as e:
        print(f"ERREUR: {e}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(facts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Vérifier que le script s'importe et affiche l'usage (sans réseau)**

Run: `py D:/LoL/.claude/skills/coach-lol/scripts/coach.py`
Expected: `Usage: py coach.py <matchId>` sur stderr, code de sortie 2.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/coach-lol/scripts/coach.py
git commit -m "feat(coach-lol): CLI orchestrateur -> JSON de faits"
```

---

## Task 8: `SKILL.md` (comportement du modèle)

**Files:**
- Create: `D:/LoL/.claude/skills/coach-lol/SKILL.md`

- [ ] **Step 1: Écrire le SKILL.md**

`D:/LoL/.claude/skills/coach-lol/SKILL.md`
````markdown
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
````

- [ ] **Step 2: Vérifier la présence du frontmatter**

Run: `py -c "import re,io; t=open(r'D:/LoL/.claude/skills/coach-lol/SKILL.md',encoding='utf-8').read(); print('OK' if t.startswith('---') and 'name: coach-lol' in t else 'KO')"`
Expected: `OK`.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/coach-lol/SKILL.md
git commit -m "feat(coach-lol): SKILL.md (débrief auto + drill-down)"
```

---

## Task 9: Validation end-to-end sur la vraie game + fixture réelle

**Files:**
- Create: `D:/LoL/.claude/skills/coach-lol/tests/fixtures/real_7891869242_facts.json` (sortie réelle, données de l'utilisateur)

- [ ] **Step 1: Lancer le script sur la vraie game**

Run: `py D:/LoL/.claude/skills/coach-lol/scripts/coach.py 7891869242 > D:/LoL/.claude/skills/coach-lol/tests/fixtures/real_7891869242_facts.json`
Expected: fichier JSON rempli, pas d'`ERREUR:`.
Si erreur clé (403) : régénérer la clé dev dans le `.env` et relancer.
Si 404 : vérifier le match ID et le tagLine (`Niir#EUW`).

- [ ] **Step 2: Vérifier la cohérence des faits**

Run: `py -c "import json; d=json.load(open(r'D:/LoL/.claude/skills/coach-lol/tests/fixtures/real_7891869242_facts.json',encoding='utf-8')); print(d['match_info']); print('morts:', len(d['deaths']))"`
Expected: champ/rôle plausibles, nombre de morts == deaths du `match_info.kda`.

- [ ] **Step 3: Sanity check humain**

Invoquer le skill `coach-lol` avec le match ID `7891869242` et lire le débrief produit. Vérifier que :
- le champion et le rôle correspondent à la game,
- les morts citées ont des minutes plausibles,
- les 2-3 axes sont concrets et non génériques.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/coach-lol/tests/fixtures/real_7891869242_facts.json
git commit -m "test(coach-lol): fixture réelle (game 7891869242) + validation e2e"
```

---

## Notes d'exécution

- **Secrets** : la clé n'apparaît jamais dans le code ni les commits — uniquement dans `D:/LoL/.env` (gitignoré).
- **Clé dev vs Personal** : aucun changement de code au passage à la clé Personal — seule la valeur dans `.env` change.
- **Schéma réel vs fixtures** : si la game réelle révèle un champ manquant/différent (Task 9), corriger l'`analyze.py` concerné, mettre à jour la fixture synthétique et re-tester avant de continuer.
