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


def test_headers_include_browser_user_agent():
    # Sans User-Agent navigateur, Cloudflare bloque (error code 1010). Régression à verrouiller.
    h = riot_client._headers("RGAPI-test")
    assert h["X-Riot-Token"] == "RGAPI-test"
    assert "Mozilla" in h["User-Agent"]
