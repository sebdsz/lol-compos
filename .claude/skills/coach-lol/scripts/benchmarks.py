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
