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
