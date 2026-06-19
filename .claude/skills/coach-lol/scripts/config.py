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
