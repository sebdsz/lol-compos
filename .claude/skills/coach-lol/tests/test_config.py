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
