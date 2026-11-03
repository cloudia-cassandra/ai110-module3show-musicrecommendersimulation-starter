from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_advanced_features_add_points_and_reasons():
    rec = make_small_recommender()
    song = rec.songs[0]
    song.mood_tags = ["sunny", "uplifting"]
    song.popularity = 80
    base = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)
    advanced = UserProfile(
        favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False,
        mood_tags=["sunny"], target_popularity=80,
    )

    base_text = rec.explain_recommendation(base, song)
    advanced_text = rec.explain_recommendation(advanced, song)

    assert "mood tags sunny" in advanced_text
    assert "popularity 80" in advanced_text
    assert float(advanced_text.split()[1].rstrip(":")) > float(base_text.split()[1].rstrip(":"))


def test_scoring_modes_change_the_ranking():
    from src.recommender import GENRE_FIRST, MOOD_FIRST

    # Genre points at the lofi song, mood points at the pop song, and energy ties them
    user = UserProfile(favorite_genre="lofi", favorite_mood="happy", target_energy=0.6, likes_acoustic=False)
    songs = make_small_recommender().songs

    genre_first = Recommender(songs, mode=GENRE_FIRST).recommend(user, k=1)[0]
    mood_first = Recommender(songs, mode=MOOD_FIRST).recommend(user, k=1)[0]

    assert genre_first.genre == "lofi"
    assert mood_first.mood == "happy"


def test_diversity_penalty_avoids_repeating_an_artist():
    def song(id, artist, genre, energy):
        return Song(id=id, title=f"Song {id}", artist=artist, genre=genre, mood="happy",
                    energy=energy, tempo_bpm=120, valence=0.8, danceability=0.8, acousticness=0.2)

    # Two strong songs by the same artist, and a slightly weaker one by someone else
    songs = [song(1, "Same Artist", "pop", 0.8), song(2, "Same Artist", "pop", 0.75),
             song(3, "Other Artist", "pop", 0.6)]
    user = UserProfile(favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False)

    plain = Recommender(songs).recommend(user, k=2)
    diverse = Recommender(songs, diverse=True).recommend(user, k=2)

    assert [s.artist for s in plain] == ["Same Artist", "Same Artist"]
    assert [s.artist for s in diverse] == ["Same Artist", "Other Artist"]
