# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Challenge 1: add 5 or more advanced song attributes to the dataset, and update the scoring logic so recommendations take them into account. The agent was Claude Code in VS Code, which edits files and runs commands on its own.

**Prompts used:**

> Introduce 5 or more complex attributes to your dataset that are not currently present in the baseline data, such as Song Popularity (0-100), Release Decade, or Detailed Mood Tags (e.g., "nostalgic," "aggressive," "euphoric"). Update both data/songs.csv and the scoring logic in src/recommender.py so scoring accounts for the new attributes.

Earlier prompts that shaped this one:
- *"Suggest new numerical features, like Danceability or Acousticness, to add more depth to the simulation."* The agent suggested instrumentalness, release year and popularity as the most useful.
- *"Give me point-weighting strategies."* The agent recommended keeping any new weights at 0.5 or less, so they refine the core recipe instead of overpowering it.

**What did the agent generate or change?**

| File | Change |
|---|---|
| `data/songs.csv` | Added 5 columns to all 20 songs: `popularity` (0–100), `release_decade` (1960–2020), `mood_tags` (3 tags separated by `;`, e.g. `cozy;rainy;calm`), `instrumentalness` (0–1) and `speechiness` (0–1). The original 10 columns weren't touched. |
| `src/recommender.py` | **Weights:** new constants (popularity 0.5, decade 0.75, 0.5 per mood tag up to 1.0, instrumental 0.75, speechiness 0.5). **`Song`:** 5 new fields with defaults, so older code that creates songs still works. **`UserProfile`:** 5 new optional preferences. **`load_songs`:** converts the new columns and splits tags into a list. **`score_song`:** 5 new rules, each with its own reason line. |
| `src/main.py` | Added 3 profiles that use the new features: *Deep-Cut Study Session*, *Throwback Heartbreak* and *Rap Hits*. |
| `tests/test_recommender.py` | Added a test checking that mood tags and popularity add points and show up in the explanation. |
| `model_card.md`, `README.md` | Documented the new features and their points. |

**Design choices the agent made:**
- **Every new rule is optional.** It's skipped unless the user sets that preference, so the 9 existing profiles score exactly the same as before.
- **Decade uses a 30-year tolerance.** The same decade gets full points, one decade away gets ⅔ and two decades away gets ⅓.
- **Mood tags give partial matches.** Each song has 3 detailed tags, so a "melancholic" listener can still match *Paper Hearts* (mood "sad") through its "heartbroken" tag.

**What did you verify or fix manually?**

Checks run after the change:
- **The original data is unchanged.** I compared the first 10 columns of the CSV against the last commit, and they're identical.
- **Old results are unchanged.** The output for the 9 existing profiles is identical to the documented run in `model_card.md`.
- **Tests pass:** 3 passed (2 original + 1 new).
- **The math adds up.** *Library Rain* in the Deep-Cut Study Session profile: 2.0 + 1.0 + 1.90 + 0.43 + 0.38 + 1.00 + 0.68 = 7.39, which matches the printed score.
- **Results make sense:**
  - *Gray Morning Blues* (1960s, rainy, heartbroken) wins *Throwback Heartbreak* by more than 2 points.
  - *Concrete Crown*, the only song with a lot of rapping (speechiness 0.33), wins *Rap Hits*.

Things I noticed that need human judgment:
- **Popularity barely matters.** With a 0.5 weight spread over a 0–100 scale, a 25-point gap only costs 0.13 points. *Library Rain* (popularity 55) still beats less popular songs for a "deep cuts" listener.
- **One questionable pick.** *Library Rain*, an instrumental lofi track, shows up at #4 for *Throwback Heartbreak* because its energy and "rainy" tag match, even though the listener wants vocals.
- **Zero-point reasons are still printed.** Lines like "from the 2020s vs target 1960s (+0.00)" add clutter, but I kept them because the other numeric rules also show zero-point lines.
- **The new values are estimates.** Like the original 10 values, they're picked to fit each genre's typical sound, not measured from real audio.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

A lightweight **Strategy pattern**. Each ranking mode is an interchangeable "strategy" object that gets passed into the scoring code. The scoring code doesn't know or care which mode it's running; it just uses the weights it's handed.

**How did AI help you brainstorm or implement it?**

I gave Claude Code the Challenge 2 prompt ("build two or more ranking strategies… brainstorm a design pattern like a simple Strategy pattern that keeps your code modular") with `recommender.py` attached. It compared four options:

| Option | Idea | Verdict |
|---|---|---|
| `if mode == "mood-first": ...` inside `score_song` | One function with branches for each mode | ❌ Every new mode means editing the scoring function, and the branches repeat the same math |
| One function per mode (`score_genre_first`, `score_mood_first`, …) | Separate scoring functions | ❌ Copies all 10 rules into each function, so a bug fix has to be made 3 times |
| A class hierarchy (`ScoringStrategy` base class + subclasses) | Classic object-oriented Strategy | ⚠️ Works, but it's heavy when the modes only differ by numbers |
| **A weights object passed into one scoring function** | Each mode is a frozen dataclass of weights | ✅ **Chosen:** the rules are written once, and each mode only lists what it changes |

The key point the AI raised: **my modes don't score differently, they *weight* differently.** All three use the same 10 rules (genre match, energy closeness, and so on); only the points change. So the strategy can just be data, a set of weights, instead of a separate algorithm. If a future mode needed a truly different rule (for example, a diversity penalty), that's when switching to a class hierarchy would make sense.

The AI also suggested:
- Making the modes **frozen** (read-only), so a mode can't be accidentally changed while songs are being scored.
- Giving every mode the **same defaults as the original recipe**, so each mode only lists the weights it changes.
- Keeping **genre-first as the default everywhere**, so existing code, tests and documented outputs keep working without changes.

**How does the pattern appear in your final code?**

- **The strategy:** `ScoringMode` in `src/recommender.py`, a frozen dataclass with one weight per rule plus a `name` and `description`.
- **The concrete strategies:** `GENRE_FIRST` (the original 2.0 / 1.0 recipe), `MOOD_FIRST` (mood 2.0, genre 1.0, more weight on valence and mood tags) and `ENERGY_FOCUSED` (energy 4.0, genre and mood 0.5 each).
- **The registry:** `MODES`, a dict from mode name to mode object, which is what `main.py` uses to look modes up.
- **The context that uses the strategy:** `score_song(user_prefs, song, mode)`, `recommend_songs(..., mode=...)` and `Recommender(songs, mode=...)`. Each one defaults to `GENRE_FIRST`.
- **Switching modes:** in `main.py`, change `DEFAULT_MODE` or run `python -m src.main --mode mood-first`. A misspelled mode name is rejected with a list of valid choices.

Adding a fourth mode takes one line plus adding it to `MODES`, with no changes to the scoring code:
```python
DISCOVERY = ScoringMode("discovery", "Favors less popular songs.", popularity=2.0)
```

**Verification:**
- **4 tests pass.** That includes a new test where the same user gets a lofi song first in genre-first mode and a happy pop song first in mood-first mode.
- **Genre-first output is identical** to the previous version for all 12 profiles; the only addition is a "Scoring mode" line at the top.
- **The modes behave differently in the expected ways:**
  - *High-Energy Pop:* genre-first ranks *Gym Hero* #2, and mood-first and energy-focused both move the happier *Rooftop Lights* up to #2.
  - *Energetic but Sad:* energy-focused drops the quiet *Paper Hearts* from #1 and puts loud songs first.
- **One questionable result:** in mood-first mode, *Library Rain* (instrumental lofi) climbs to #3 for *Throwback Heartbreak* on its "rainy" tag alone. That's a sign the bigger tag bonus (0.75) may be too strong.

---

## Diversity and Fairness Logic (Challenge 3)

**What task did you give the agent?**

Add a "diversity penalty" so the top results don't fill up with songs from the same artist or genre.

**Prompt used:**

> In `src/recommender.py`, add an optional diversity step to the ranking. Build the top-k list one song at a time. At each step, pick the remaining song with the highest **adjusted** score: its normal score minus 1.5 for each song by the **same artist** already in the list, and minus 0.75 for each song in the **same genre** already in the list. When a penalty applies, add a reason like "diversity: artist LoRoom already in list (-1.50)". Keep it off by default so existing outputs and tests don't change, add a `--diverse` flag to `main.py`, and verify that (a) with it off, the output is identical, (b) with it on, Chill Lofi's top 5 no longer repeats an artist, and (c) each printed score equals the original score minus the penalties listed.

**Key design decision:** the penalty lives in the **ranking** step, not in `score_song`. Whether a song "repeats an artist" depends on which songs are already in the list, and `score_song` judges one song at a time. So the new `diversify()` function re-ranks the scored list *greedily*: it picks the best song, updates the artist and genre counts, re-checks every remaining song with the new penalties, and repeats until it has k songs.

**What did the agent generate or change?**

| File | Change |
|---|---|
| `src/recommender.py` | `ARTIST_REPEAT_PENALTY = 1.5` and `GENRE_REPEAT_PENALTY = 0.75`; a new `diversify()` function; `recommend_songs(..., diverse=False)` and `Recommender(..., diverse=False)`. `Recommender.recommend` now goes through `recommend_songs`, so both paths share one ranking. |
| `src/main.py` | A `--diverse` flag, which also prints "Diversity penalty: on" at the top. Works with any `--mode`. |
| `tests/test_recommender.py` | A new test: two strong songs by the same artist and one weaker song by another artist. Without diversity, the top 2 are both by the same artist; with it, the other artist gets the #2 spot. |

**Why the penalties are 1.5 and 0.75:** a repeat artist should cost more than a near-miss on energy (energy 0.25 off costs 0.5), but less than a genre match (2.0). That way a clearly better song by the same artist can still make the list. A repeat genre costs half as much, because a lofi fan still *wants* several lofi songs.

**What did you verify or fix manually?**

- **Off by default:** with `--diverse` off, the output is identical to the previous commit in all 3 modes, and all 5 tests pass.
- **The math adds up:** for every song in every profile, the printed score equals the original score minus the listed penalties.
- **It does its job.** Chill Lofi before and after:

  | | Before | After `--diverse` |
  |---|---|---|
  | Top 5 | Library Rain, Midnight Coding, **Focus Flow**, Spacewalk Thoughts, Coffee Shop Stories | Library Rain, Midnight Coding, Spacewalk Thoughts, Coffee Shop Stories, **Gray Morning Blues** |
  | Most songs by one artist | 2 (LoRoom) | 1 |
  | Most songs in one genre | 3 (lofi) | 2 |

  *Focus Flow* dropped from 4.29 to 1.29: −1.50 because LoRoom was already in the list, and −1.50 because 2 lofi songs were already there.
- **Across all 12 profiles:** 7 lists changed, and no list repeats an artist anymore.

**Trade-offs I noticed:**
- **Diversity can cost relevance.** For *Rap Hits* and *Messy Input*, *Night Drive Loop* (a repeat Neon Echo song) was replaced by *Storm Runner*, an intense rock song that's a worse fit for those listeners. For Chill Lofi, *Gray Morning Blues* (melancholic blues) entered at #5. It's calm and acoustic, but it isn't really study music.
- **Fairness for artists:** without the penalty, LoRoom and Neon Echo, the only artists with two songs, could take two of the five spots. With it, five different artists get exposure. In a real app this matters, because being recommended means being heard and paid.
- **Small catalog:** with only 20 songs, "the next most diverse" song is sometimes not very good. A bigger catalog would let diversity help without hurting fit.

---

## Visual Summary Table (Challenge 4)

**What task did you give the agent?**

Make the terminal output easier to read with a formatted table that still shows *why* each song scored what it did.

**Prompt used:**

> Suggest a way to display my top recommendations in the terminal as a table, using tabulate or simple ASCII formatting. The table **must include the reasons for each score**, one reason per line inside the cell rather than squeezed onto one line, along with the rank, song title, artist and final score. Keep the current detailed output as the default and add a `--table` flag. Avoid a new dependency if plain Python can do it cleanly.

**tabulate or plain ASCII?** The agent first checked whether `tabulate` was installed. It wasn't, in either the system Python or `.venv`. Using it would have meant adding it to `requirements.txt`, and `python -m src.main --table` would crash for anyone who skipped `pip install`. Because each cell is just a list of lines, a small ASCII builder handles multi-line reasons in about 20 lines with no new dependency, so the agent went with that.

**What did the agent generate or change?**

| File | Change |
|---|---|
| `src/main.py` | `format_table()`, a generic ASCII table builder where each cell can hold several lines, with right-aligned number columns. `print_recommendation_table()` builds the rows (rank; title plus "by artist"; score; one reason per line, wrapped at 48 characters) and adds a "Top pick" summary line with the lead over #2. A new `--table` flag works with `--mode` and `--diverse`. |
| `README.md` | Added a sample table under Sample Recommendation Output. |

**Sample output:**

```
High-Energy Pop
Profile: genre='pop', mood='happy', energy=0.8
+---+------------------+-------+------------------------------------+
| # | Song             | Score | Reasons                            |
+===+==================+=======+====================================+
| 1 | Sunrise City     |  4.96 | genre matches pop (+2.0)           |
|   | by Neon Echo     |       | mood matches happy (+1.0)          |
|   |                  |       | energy 0.82 vs target 0.80 (+1.96) |
+---+------------------+-------+------------------------------------+
| 2 | Gym Hero         |  3.74 | genre matches pop (+2.0)           |
|   | by Max Pulse     |       | energy 0.93 vs target 0.80 (+1.74) |
+---+------------------+-------+------------------------------------+
| 3 | Rooftop Lights   |  2.92 | mood matches happy (+1.0)          |
|   | by Indigo Parade |       | energy 0.76 vs target 0.80 (+1.92) |
+---+------------------+-------+------------------------------------+
| 4 | Fuego Lento      |  2.00 | energy 0.80 vs target 0.80 (+2.00) |
|   | by Los Caminos   |       |                                    |
+---+------------------+-------+------------------------------------+
| 5 | Concrete Crown   |  1.96 | energy 0.78 vs target 0.80 (+1.96) |
|   | by K-Verse       |       |                                    |
+---+------------------+-------+------------------------------------+
Top pick: Sunrise City, 1.22 points ahead of #2
```

**What did you verify or fix manually?**

- **The default output is unchanged.** Without `--table`, the output is identical to before, so the README and model card samples still match. All 5 tests pass.
- **Every reason is shown.** Each table lists every reason line that the detailed view prints, including "diversity: …" penalties when `--diverse` is on.
- **It fits the terminal.** The widest table line across all 12 profiles is 83 characters. Only one long profile line (*Deep-Cut Study Session*) is wider, and it simply wraps.
- **The summary line is correct.** 4.96 − 3.74 = 1.22 for High-Energy Pop.
- **One limitation:** the column widths adjust to the longest text in each table, so different profiles' tables have slightly different widths.
