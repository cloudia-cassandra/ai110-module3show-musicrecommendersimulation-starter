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

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
