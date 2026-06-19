"""Client API Riot minimal (stdlib). I/O réseau isolée ici."""
import json
import urllib.request
import urllib.parse
import urllib.error

import config

_CLUSTER = f"https://{config.REGION_CLUSTER}.api.riotgames.com"

# Sans un User-Agent navigateur, l'edge Cloudflare de Riot bloque urllib
# (réponse "error code: 1010"). Indispensable pour que les appels passent.
_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


class RiotError(Exception):
    pass


def _headers(api_key):
    return {
        "X-Riot-Token": api_key,
        "User-Agent": _BROWSER_UA,
        "Accept": "application/json",
    }


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
    req = urllib.request.Request(url, headers=_headers(api_key))
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
