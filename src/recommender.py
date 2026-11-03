import csv
from collections import Counter
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict, field

DECADE_TOLERANCE = 30       # songs 30+ years from the target decade earn 0
MAX_TAGS_COUNTED = 2        # mood tag points stop after this many matches

# Diversity re-ranking: subtracted once per song already picked with the same artist / genre
ARTIST_REPEAT_PENALTY = 1.5
GENRE_REPEAT_PENALTY = 0.75

@dataclass(frozen=True)
class ScoringMode:
    """A ranking strategy: one set of weights that score_song can be run with."""
    name: str
    description: str
    genre: float = 2.0
    mood: float = 1.0
    energy: float = 2.0
    valence: float = 1.0
    acoustic: float = 0.5
    # Advanced feature weights, kept small so they refine rather than override the core recipe
    popularity: float = 0.5
    decade: float = 0.75
    tag: float = 0.5            # per matching mood tag
    instrumental: float = 0.75
    speechiness: float = 0.5

# Built-in strategies (see model_card.md for the reasoning behind the weights)
GENRE_FIRST = ScoringMode(
    "genre-first", "Genre is the strongest signal; the original recipe.",
)
MOOD_FIRST = ScoringMode(
    "mood-first", "Mood and feel outrank genre; good for 'I want something sad' listeners.",
    genre=1.0, mood=2.0, valence=1.5, tag=0.75,
)
ENERGY_FOCUSED = ScoringMode(
    "energy-focused", "Energy level decides; labels only break ties.",
    genre=0.5, mood=0.5, energy=4.0,
)

MODES = {mode.name: mode for mode in (GENRE_FIRST, MOOD_FIRST, ENERGY_FOCUSED)}

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
    popularity: int = 50
    release_decade: int = 2020
    mood_tags: List[str] = field(default_factory=list)
    instrumentalness: float = 0.0
    speechiness: float = 0.0

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
    target_popularity: Optional[int] = None
    target_decade: Optional[int] = None
    mood_tags: Optional[List[str]] = None
    wants_instrumental: Optional[bool] = None
    target_speechiness: Optional[float] = None

    def to_prefs(self) -> Dict:
        """Converts the profile into the dict format used by score_song."""
        return {
            "genre": self.favorite_genre,
            "mood": self.favorite_mood,
            "energy": self.target_energy,
            "valence": self.target_valence,
            "likes_acoustic": self.likes_acoustic,
            "popularity": self.target_popularity,
            "decade": self.target_decade,
            "mood_tags": self.mood_tags,
            "wants_instrumental": self.wants_instrumental,
            "speechiness": self.target_speechiness,
        }

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song], mode: ScoringMode = GENRE_FIRST, diverse: bool = False):
        self.songs = songs
        self.mode = mode
        self.diverse = diverse

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs for the user, ranked by score_song from highest to lowest."""
        by_id = {song.id: song for song in self.songs}
        results = recommend_songs(
            user.to_prefs(), [asdict(song) for song in self.songs], k, self.mode, self.diverse
        )
        return [by_id[song["id"]] for song, _, _ in results]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a readable string with the song's score and the reasons behind it."""
        score, reasons = score_song(user.to_prefs(), asdict(song), self.mode)
        if not reasons:
            return f"Score {score:.2f}: no strong matches with your preferences"
        return f"Score {score:.2f}: " + "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    int_fields = ["id", "popularity", "release_decade"]
    float_fields = ["energy", "tempo_bpm", "valence", "danceability", "acousticness",
                    "instrumentalness", "speechiness"]
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for name in int_fields:
                row[name] = int(row[name])
            for name in float_fields:
                row[name] = float(row[name])
            # "cozy;rainy;calm" -> ["cozy", "rainy", "calm"]
            row["mood_tags"] = [tag.strip().lower() for tag in row["mood_tags"].split(";") if tag.strip()]
            songs.append(row)
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs

def score_song(user_prefs: Dict, song: Dict, mode: ScoringMode = GENRE_FIRST) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences, using the weights of the given mode.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons = []

    genre = user_prefs.get("genre")
    if genre and song["genre"].lower() == genre.lower():
        score += mode.genre
        reasons.append(f"genre matches {genre} (+{mode.genre:.1f})")

    mood = user_prefs.get("mood")
    if mood and song["mood"].lower() == mood.lower():
        score += mode.mood
        reasons.append(f"mood matches {mood} (+{mode.mood:.1f})")

    # Closeness scores: 1.0 for an exact match, falling toward 0 as the gap grows
    target_energy = user_prefs.get("energy")
    if target_energy is not None:
        points = mode.energy * (1 - abs(target_energy - song["energy"]))
        score += points
        reasons.append(f"energy {song['energy']:.2f} vs target {target_energy:.2f} (+{points:.2f})")

    target_valence = user_prefs.get("valence")
    if target_valence is not None:
        points = mode.valence * (1 - abs(target_valence - song["valence"]))
        score += points
        reasons.append(f"valence {song['valence']:.2f} vs target {target_valence:.2f} (+{points:.2f})")

    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        fit = song["acousticness"] if likes_acoustic else 1 - song["acousticness"]
        points = mode.acoustic * fit
        score += points
        label = "acoustic" if likes_acoustic else "non-acoustic"
        reasons.append(f"{label} fit (+{points:.2f})")

    # Advanced features: each is skipped unless the user sets a preference for it
    target_popularity = user_prefs.get("popularity")
    if target_popularity is not None:
        points = mode.popularity * (1 - abs(target_popularity - song["popularity"]) / 100)
        score += points
        reasons.append(f"popularity {song['popularity']} vs target {target_popularity} (+{points:.2f})")

    target_decade = user_prefs.get("decade")
    if target_decade is not None:
        closeness = max(0.0, 1 - abs(target_decade - song["release_decade"]) / DECADE_TOLERANCE)
        points = mode.decade * closeness
        score += points
        reasons.append(f"from the {song['release_decade']}s vs target {target_decade}s (+{points:.2f})")

    wanted_tags = user_prefs.get("mood_tags")
    if wanted_tags:
        wanted = {tag.strip().lower() for tag in wanted_tags}
        matched = [tag for tag in song["mood_tags"] if tag in wanted]
        if matched:
            points = mode.tag * min(len(matched), MAX_TAGS_COUNTED)
            score += points
            reasons.append(f"mood tags {', '.join(matched)} (+{points:.2f})")

    wants_instrumental = user_prefs.get("wants_instrumental")
    if wants_instrumental is not None:
        fit = song["instrumentalness"] if wants_instrumental else 1 - song["instrumentalness"]
        points = mode.instrumental * fit
        score += points
        label = "instrumental" if wants_instrumental else "vocal"
        reasons.append(f"{label} fit (+{points:.2f})")

    target_speechiness = user_prefs.get("speechiness")
    if target_speechiness is not None:
        points = mode.speechiness * (1 - abs(target_speechiness - song["speechiness"]))
        score += points
        reasons.append(f"speechiness {song['speechiness']:.2f} vs target {target_speechiness:.2f} (+{points:.2f})")

    return score, reasons

def diversify(ranked: List[Tuple[Dict, float, List[str]]], k: int) -> List[Tuple[Dict, float, List[str]]]:
    """Re-ranks songs one pick at a time, penalizing artists and genres already in the list."""
    picked = []
    artist_counts, genre_counts = Counter(), Counter()
    remaining = list(ranked)

    def adjusted(item):
        song, score, _ = item
        return (score
                - ARTIST_REPEAT_PENALTY * artist_counts[song["artist"]]
                - GENRE_REPEAT_PENALTY * genre_counts[song["genre"]])

    while remaining and len(picked) < k:
        # max() keeps the first of any ties, so equal scores stay in their original order
        best = max(remaining, key=adjusted)
        remaining.remove(best)
        song, _, reasons = best

        penalties = []
        if artist_counts[song["artist"]]:
            cost = ARTIST_REPEAT_PENALTY * artist_counts[song["artist"]]
            penalties.append(f"diversity: artist {song['artist']} already in list (-{cost:.2f})")
        if genre_counts[song["genre"]]:
            cost = GENRE_REPEAT_PENALTY * genre_counts[song["genre"]]
            penalties.append(f"diversity: genre {song['genre']} already in list (-{cost:.2f})")

        picked.append((song, adjusted(best), reasons + penalties))
        artist_counts[song["artist"]] += 1
        genre_counts[song["genre"]] += 1

    return picked

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    mode: ScoringMode = GENRE_FIRST, diverse: bool = False) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    ranked = sorted(
        ((song, *score_song(user_prefs, song, mode)) for song in songs),
        key=lambda item: item[1],
        reverse=True,
    )
    if diverse:
        ranked = diversify(ranked, k)
    return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]
