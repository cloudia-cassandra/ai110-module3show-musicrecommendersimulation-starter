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
import textwrap

from src.recommender import MODES, GENRE_FIRST, load_songs, recommend_songs

WIDTH = 60
REASON_WIDTH = 48   # reasons longer than this wrap onto the next line of the cell

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


def format_table(headers: list, rows: list, right_aligned: set) -> str:
    """Builds an ASCII table where each cell is a list of lines, so cells can span several rows."""
    widths = [max(len(line) for cell in [[header]] + [row[i] for row in rows] for line in cell)
              for i, header in enumerate(headers)]
    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"

    def render(cells: list) -> list:
        lines = []
        for line_no in range(max(len(cell) for cell in cells)):
            parts = []
            for i, cell in enumerate(cells):
                text = cell[line_no] if line_no < len(cell) else ""
                parts.append(text.rjust(widths[i]) if i in right_aligned else text.ljust(widths[i]))
            lines.append("| " + " | ".join(parts) + " |")
        return lines

    out = [border, *render([[header] for header in headers]), border.replace("-", "=")]
    for row in rows:
        out += render(row) + [border]
    return "\n".join(out)


def print_recommendation_table(name: str, user_prefs: dict, recommendations: list) -> None:
    """Prints the recommendations as a table with rank, song, score, and every scoring reason."""
    profile = ", ".join(f"{key}={value!r}" for key, value in user_prefs.items()) or "(none)"
    print(f"\n{name}")
    print(f"Profile: {profile}")

    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reasons = explanation.split("; ") if explanation else ["no matching preferences"]
        wrapped = [line for reason in reasons
                   for line in textwrap.wrap(reason, REASON_WIDTH, subsequent_indent="  ")]
        rows.append([[str(rank)], [song["title"], f"by {song['artist']}"], [f"{score:.2f}"], wrapped])
    print(format_table(["#", "Song", "Score", "Reasons"], rows, right_aligned={0, 2}))

    if len(recommendations) > 1:
        (top, top_score, _), (_, second_score, _) = recommendations[0], recommendations[1]
        print(f"Top pick: {top['title']}, {top_score - second_score:.2f} points ahead of #2")


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--mode", choices=MODES, default=DEFAULT_MODE, help="ranking strategy to use")
    parser.add_argument("--diverse", action="store_true",
                        help="penalize repeat artists and genres in the top results")
    parser.add_argument("--table", action="store_true",
                        help="show each profile's results as a summary table")
    args = parser.parse_args()
    mode = MODES[args.mode]

    songs = load_songs("data/songs.csv")
    print(f"Scoring mode: {mode.name} ({mode.description})")
    if args.diverse:
        print("Diversity penalty: on (repeat artists and genres lose points)")

    for name, user_prefs in {**PROFILES, **EDGE_CASE_PROFILES, **ADVANCED_PROFILES}.items():
        recommendations = recommend_songs(user_prefs, songs, k=5, mode=mode, diverse=args.diverse)
        if args.table:
            print_recommendation_table(name, user_prefs, recommendations)
        else:
            print_recommendations(name, user_prefs, recommendations)


if __name__ == "__main__":
    main()
