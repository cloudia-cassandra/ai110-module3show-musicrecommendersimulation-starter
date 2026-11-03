"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs

Run from the project root with: python -m src.main
"""

from src.recommender import load_songs, recommend_songs

WIDTH = 60


def print_recommendations(user_prefs: dict, recommendations: list) -> None:
    """Prints each recommendation with its title, score, and scoring reasons."""
    profile = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    print()
    print("=" * WIDTH)
    print(f"Top {len(recommendations)} recommendations")
    print(f"Profile: {profile}")
    print("=" * WIDTH)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print()
        print(f"{rank}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f}")
        print("   Reasons:")
        for reason in explanation.split("; "):
            print(f"     - {reason}")

    print()
    print("=" * WIDTH)


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Default profile: an upbeat pop listener
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations(user_prefs, recommendations)


if __name__ == "__main__":
    main()
