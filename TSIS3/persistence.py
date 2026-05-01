import json
from pathlib import Path

SETTINGS_FILE = Path("settings.json")
LEADERBOARD_FILE = Path("leaderboard.json")

DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "blue",
    "difficulty": "normal"
}


def load_settings():
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            settings = json.load(file)
    except json.JSONDecodeError:
        settings = DEFAULT_SETTINGS.copy()

    for key, value in DEFAULT_SETTINGS.items():
        settings.setdefault(key, value)

    return settings


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def load_leaderboard():
    if not LEADERBOARD_FILE.exists():
        save_leaderboard([])
        return []

    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            return []
    except json.JSONDecodeError:
        return []


def save_leaderboard(scores):
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as file:
        json.dump(scores, file, indent=4)


def add_score(name, score, distance, coins):
    scores = load_leaderboard()

    scores.append({
        "name": name,
        "score": score,
        "distance": distance,
        "coins": coins
    })

    scores.sort(key=lambda item: item["score"], reverse=True)
    scores = scores[:10]

    save_leaderboard(scores)