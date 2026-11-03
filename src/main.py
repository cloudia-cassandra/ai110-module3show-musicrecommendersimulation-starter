"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs

Run from the project root with: python -m src.main
Pick a scoring mode with:        python -m src.main --mode mood-first
"""

import argparse

from src.recommender import MODES, GENRE_FIRST, load_songs, recommend_songs

WIDTH = 60

# Change this to switch the default mode: "genre-first", "mood-first" or "energy-focused"
DEFAULT_MODE = GENRE_FIRST.name

# Distinct listener types the recommender should handle well
PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.92, "valence": 0.4, "likes_acoustic": False},
}

# Adversarial profiles designed to trick the scoring logic
EDGE_CASE_PROFILES = {
    "Conflicting: Energetic but Sad": {"genre": "folk", "mood": "sad", "energy": 0.9},
    "Acoustic Headbanger": {"genre": "metal", "mood": "angry", "energy": 0.95, "likes_acoustic": True},
    "Genre Not in Catalog": {"genre": "k-pop", "mood": "happy", "energy": 0.7},
    "Messy Input": {"genre": " Pop ", "mood": "HAPPY", "energy": 0.8},
    "Out-of-Range Energy": {"genre": "classical", "mood": "peaceful", "energy": 1.5},
    "Empty Profile": {},
}

# Profiles that use the advanced features (popularity, decade, mood tags, instrumentalness, speechiness)
ADVANCED_PROFILES = {
    "Deep-Cut Study Session": {
        "genre": "lofi", "mood": "chill", "energy": 0.4, "likes_acoustic": True,
        "wants_instrumental": True, "popularity": 30, "mood_tags": ["rainy", "calm"],
    },
    "Throwback Heartbreak": {
        "mood": "melancholic", "energy": 0.35, "decade": 1960,
        "mood_tags": ["heartbroken", "rainy"], "wants_instrumental": False,
    },
    "Rap Hits": {"genre": "hip-hop", "energy": 0.8, "speechiness": 0.3, "popularity": 80},
}


def print_recommendations(name: str, user_prefs: dict, recommendations: list) -> None:
    """Prints each recommendation with its title, score, and scoring reasons."""
    profile = ", ".join(f"{key}={value!r}" for key, value in user_prefs.items()) or "(none)"
    print()
    print("=" * WIDTH)
    print(f"{name}: top {len(recommendations)} recommendations")
    print(f"Profile: {profile}")
    print("=" * WIDTH)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print()
        print(f"{rank}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f}")
        print("   Reasons:")
        reasons = explanation.split("; ") if explanation else ["no matching preferences"]
        for reason in reasons:
            print(f"     - {reason}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--mode", choices=MODES, default=DEFAULT_MODE, help="ranking strategy to use")
    mode = MODES[parser.parse_args().mode]

    songs = load_songs("data/songs.csv")
    print(f"Scoring mode: {mode.name} ({mode.description})")

    for name, user_prefs in {**PROFILES, **EDGE_CASE_PROFILES, **ADVANCED_PROFILES}.items():
        recommendations = recommend_songs(user_prefs, songs, k=5, mode=mode)
        print_recommendations(name, user_prefs, recommendations)


if __name__ == "__main__":
    main()
