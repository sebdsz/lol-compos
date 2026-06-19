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
