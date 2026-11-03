import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# Scoring weights (see model_card.md for the reasoning behind each)
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 2.0
VALENCE_WEIGHT = 1.0
ACOUSTIC_WEIGHT = 0.5

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: Optional[float] = None

    def to_prefs(self) -> Dict:
        """Converts the profile into the dict format used by score_song."""
        return {
            "genre": self.favorite_genre,
            "mood": self.favorite_mood,
            "energy": self.target_energy,
            "valence": self.target_valence,
            "likes_acoustic": self.likes_acoustic,
        }

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        prefs = user.to_prefs()
        ranked = sorted(
            self.songs,
            key=lambda song: score_song(prefs, asdict(song))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        score, reasons = score_song(user.to_prefs(), asdict(song))
        if not reasons:
            return f"Score {score:.2f}: no strong matches with your preferences"
        return f"Score {score:.2f}: " + "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    float_fields = ["energy", "tempo_bpm", "valence", "danceability", "acousticness"]
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons = []

    genre = user_prefs.get("genre")
    if genre and song["genre"].lower() == genre.lower():
        score += GENRE_WEIGHT
        reasons.append(f"genre matches {genre} (+{GENRE_WEIGHT:.1f})")

    mood = user_prefs.get("mood")
    if mood and song["mood"].lower() == mood.lower():
        score += MOOD_WEIGHT
        reasons.append(f"mood matches {mood} (+{MOOD_WEIGHT:.1f})")

    # Closeness scores: 1.0 for an exact match, falling toward 0 as the gap grows
    target_energy = user_prefs.get("energy")
    if target_energy is not None:
        points = ENERGY_WEIGHT * (1 - abs(target_energy - song["energy"]))
        score += points
        reasons.append(f"energy {song['energy']:.2f} vs target {target_energy:.2f} (+{points:.2f})")

    target_valence = user_prefs.get("valence")
    if target_valence is not None:
        points = VALENCE_WEIGHT * (1 - abs(target_valence - song["valence"]))
        score += points
        reasons.append(f"valence {song['valence']:.2f} vs target {target_valence:.2f} (+{points:.2f})")

    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        fit = song["acousticness"] if likes_acoustic else 1 - song["acousticness"]
        points = ACOUSTIC_WEIGHT * fit
        score += points
        label = "acoustic" if likes_acoustic else "non-acoustic"
        reasons.append(f"{label} fit (+{points:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
