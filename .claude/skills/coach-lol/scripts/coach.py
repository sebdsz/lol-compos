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
