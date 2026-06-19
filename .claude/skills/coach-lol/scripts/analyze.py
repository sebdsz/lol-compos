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
