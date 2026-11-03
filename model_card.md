# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

The recommender gives every song in the catalog a score showing how well it fits one listener's taste, then recommends the highest-scoring songs.

**The approach in plain language:** think of it as a judge with a scorecard. The listener first describes what they're in the mood for, such as "upbeat pop, happy, fairly energetic." The judge then listens to every song in the catalog, one at a time, and fills in the same scorecard for each:
- Is it the right genre? That earns a big bonus.
- Is it the right mood? That earns a smaller bonus.
- How close is its energy to what the listener asked for? The closer it is, the more points it gets.

A song doesn't win by being the loudest or the calmest. It wins by being the *closest fit*. The judge never compares songs to each other while scoring; each song is judged on its own. Only after every song has a score does the judge line them up from highest to lowest and hand the listener the top five, with the scorecard notes for each, so the listener can see exactly why a song made the list.

This is a **content-based** approach. It looks only at what the songs are like, not at what other people listen to. Apps like Spotify also learn from millions of other listeners' plays and skips.

**What it knows about the listener:** a favorite genre, a favorite mood, how energetic they want the music (0 = very calm, 1 = very intense), and optionally how bright or dark it should sound (valence) and whether they like acoustic music.

**Final scoring recipe (maximum 6.5 points):**

| Rule | Points | Why |
|---|---|---|
| Song is in the listener's favorite genre | **+2.0** | Genre is the most stable part of someone's taste |
| Song has the listener's favorite mood | **+1.0** | Mood matters, but it partly repeats energy and valence, so it counts half as much as genre |
| Energy is close to the listener's target | **up to +2.0** | Full points for an exact match, fewer the further away it is. A song that is *closer* wins, not one that is simply louder or quieter |
| Valence (bright vs. dark) is close to the target | **up to +1.0** | Tells apart songs with the same energy but a different feel, like "happy" vs. "moody" |
| Song fits the listener's acoustic preference | **up to +0.5** | Adds texture, but kept small because acoustic songs in this catalog are usually also low-energy |

For the "closeness" rules, the points are the weight × (1 − the gap between the song and the target). For example, with a target energy of 0.40, a song at 0.35 gets 2.0 × 0.95 = 1.90 points, and a song at 0.91 gets only 0.98.

**Choosing what to recommend:** every song is scored, the list is sorted from highest to lowest, and the top 5 are shown. Each one comes with an explanation listing exactly which rules earned it points.

**Changes from the starter logic:** the starter recipe (+2.0 genre, +1.0 mood, energy closeness) is kept as the core. I added valence and acoustic fit to give the score more nuance. Tempo and danceability are not scored, because in this catalog they mostly repeat what energy already measures.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

**Weakness: the energy gap quietly treats moderate listeners differently from extreme ones.** Energy points depend on the gap between a song and the listener's target. A listener who wants middle energy (0.5) is never more than 0.47 away from any song, so energy can only separate their options by 45% of the energy weight, while a listener at 0.95 gets a spread of 80%. As a result, moderate listeners' rankings are decided mostly by the genre and mood labels, and extreme listeners' rankings mostly by energy, even though everyone uses the same weights. The catalog makes this worse: 9 of 20 songs have energy of 0.75 or higher and only 3 fall between 0.5 and 0.6, so mid-energy songs like *Velvet Hours*, *Dusty Backroads* and *Island Time* never appeared in the top 5 for any of my 9 test profiles (partly because most of those profiles also targeted extreme energy levels).

---

## 7. Evaluation  

I ran 9 user profiles through `python -m src.main` and looked at the top 5 for each. Three are typical listeners whose preferences agree with each other: an upbeat pop fan, a calm lofi studier and a dark, loud rock fan. Six are **adversarial edge cases** designed to trick the scoring logic: preferences that contradict each other, a genre the catalog doesn't have, sloppy typing, an impossible energy value, and no preferences at all. For each one I asked whether the top 5 matched what that listener would actually want, and whether the "Reasons" lines explained the ranking.

| Profile | Type | Result |
|---|---|---|
| High-Energy Pop | Typical | ✅ Mostly right; genre bias visible at #2 |
| Chill Lofi | Typical | ✅ Works well |
| Deep Intense Rock | Typical | ✅ Works well |
| Conflicting: Energetic but Sad | Conflicting preferences | ❌ Incoherent list |
| Acoustic Headbanger | Conflicting preferences | ⚠️ Acoustic preference ignored |
| Genre Not in Catalog | Missing data | ⚠️ Falls back silently |
| Messy Input | Input formatting | ❌ Bug: spaces break genre match |
| Out-of-Range Energy | Invalid input | ❌ Bug: negative points |
| Empty Profile | No preferences | ❌ Returns arbitrary songs |

### Typical profiles

#### High-Energy Pop

```
============================================================
High-Energy Pop: top 5 recommendations
Profile: genre='pop', mood='happy', energy=0.8
============================================================

1. Sunrise City by Neon Echo
   Score: 4.96
   Reasons:
     - genre matches pop (+2.0)
     - mood matches happy (+1.0)
     - energy 0.82 vs target 0.80 (+1.96)

2. Gym Hero by Max Pulse
   Score: 3.74
   Reasons:
     - genre matches pop (+2.0)
     - energy 0.93 vs target 0.80 (+1.74)

3. Rooftop Lights by Indigo Parade
   Score: 2.92
   Reasons:
     - mood matches happy (+1.0)
     - energy 0.76 vs target 0.80 (+1.92)

4. Fuego Lento by Los Caminos
   Score: 2.00
   Reasons:
     - energy 0.80 vs target 0.80 (+2.00)

5. Concrete Crown by K-Verse
   Score: 1.96
   Reasons:
     - energy 0.78 vs target 0.80 (+1.96)
```

**As expected, mostly.** *Sunrise City* is a clear #1. *Gym Hero* (pop, intense) beats *Rooftop Lights* (indie pop, happy) on the genre bonus alone, which shows genre over-prioritization.

#### Chill Lofi

```
============================================================
Chill Lofi: top 5 recommendations
Profile: genre='lofi', mood='chill', energy=0.35, likes_acoustic=True
============================================================

1. Library Rain by Paper Lanterns
   Score: 5.43
   Reasons:
     - genre matches lofi (+2.0)
     - mood matches chill (+1.0)
     - energy 0.35 vs target 0.35 (+2.00)
     - acoustic fit (+0.43)

2. Midnight Coding by LoRoom
   Score: 5.21
   Reasons:
     - genre matches lofi (+2.0)
     - mood matches chill (+1.0)
     - energy 0.42 vs target 0.35 (+1.86)
     - acoustic fit (+0.35)

3. Focus Flow by LoRoom
   Score: 4.29
   Reasons:
     - genre matches lofi (+2.0)
     - energy 0.40 vs target 0.35 (+1.90)
     - acoustic fit (+0.39)

4. Spacewalk Thoughts by Orbit Bloom
   Score: 3.32
   Reasons:
     - mood matches chill (+1.0)
     - energy 0.28 vs target 0.35 (+1.86)
     - acoustic fit (+0.46)

5. Coffee Shop Stories by Slow Stereo
   Score: 2.40
   Reasons:
     - energy 0.37 vs target 0.35 (+1.96)
     - acoustic fit (+0.45)
```

**Works well.** All three lofi songs take the top spots, followed by ambient and jazz songs with matching calm, acoustic numbers. This is the profile the catalog serves best.

#### Deep Intense Rock

```
============================================================
Deep Intense Rock: top 5 recommendations
Profile: genre='rock', mood='intense', energy=0.92, valence=0.4, likes_acoustic=False
============================================================

1. Storm Runner by Voltline
   Score: 6.35
   Reasons:
     - genre matches rock (+2.0)
     - mood matches intense (+1.0)
     - energy 0.91 vs target 0.92 (+1.98)
     - valence 0.48 vs target 0.40 (+0.92)
     - non-acoustic fit (+0.45)

2. Gym Hero by Max Pulse
   Score: 4.08
   Reasons:
     - mood matches intense (+1.0)
     - energy 0.93 vs target 0.92 (+1.98)
     - valence 0.77 vs target 0.40 (+0.63)
     - non-acoustic fit (+0.47)

3. Iron Tempest by Graveforge
   Score: 3.17
   Reasons:
     - energy 0.97 vs target 0.92 (+1.90)
     - valence 0.18 vs target 0.40 (+0.78)
     - non-acoustic fit (+0.48)

4. Concrete Crown by K-Verse
   Score: 2.98
   Reasons:
     - energy 0.78 vs target 0.92 (+1.72)
     - valence 0.58 vs target 0.40 (+0.82)
     - non-acoustic fit (+0.44)

5. Night Drive Loop by Neon Echo
   Score: 2.96
   Reasons:
     - energy 0.75 vs target 0.92 (+1.66)
     - valence 0.49 vs target 0.40 (+0.91)
     - non-acoustic fit (+0.39)
```

**Works well.** *Storm Runner* scores 6.35 of a possible 6.5. *Iron Tempest* (metal) at #3 is a sensible near-genre pick, even though the system doesn't know metal is related to rock.

### Edge-case profiles

#### Conflicting: Energetic but Sad

```
============================================================
Conflicting: Energetic but Sad: top 5 recommendations
Profile: genre='folk', mood='sad', energy=0.9
============================================================

1. Paper Hearts by Willow & Ash
   Score: 3.70
   Reasons:
     - genre matches folk (+2.0)
     - mood matches sad (+1.0)
     - energy 0.25 vs target 0.90 (+0.70)

2. Storm Runner by Voltline
   Score: 1.98
   Reasons:
     - energy 0.91 vs target 0.90 (+1.98)

3. Gym Hero by Max Pulse
   Score: 1.94
   Reasons:
     - energy 0.93 vs target 0.90 (+1.94)

4. Neon Euphoria by Pulse District
   Score: 1.90
   Reasons:
     - energy 0.95 vs target 0.90 (+1.90)

5. Iron Tempest by Graveforge
   Score: 1.86
   Reasons:
     - energy 0.97 vs target 0.90 (+1.86)
```

**Tricked.** The list is incoherent. The genre and mood bonuses (+3.0) put *Paper Hearts* at #1 even though its energy is 0.25 against a target of 0.9. Ranks 2–5 are loud songs that aren't sad at all. The system never notices that the preferences contradict each other; labels win #1 and energy wins the rest.

#### Acoustic Headbanger

```
============================================================
Acoustic Headbanger: top 5 recommendations
Profile: genre='metal', mood='angry', energy=0.95, likes_acoustic=True
============================================================

1. Iron Tempest by Graveforge
   Score: 4.97
   Reasons:
     - genre matches metal (+2.0)
     - mood matches angry (+1.0)
     - energy 0.97 vs target 0.95 (+1.96)
     - acoustic fit (+0.01)

2. Neon Euphoria by Pulse District
   Score: 2.01
   Reasons:
     - energy 0.95 vs target 0.95 (+2.00)
     - acoustic fit (+0.01)

3. Gym Hero by Max Pulse
   Score: 1.99
   Reasons:
     - energy 0.93 vs target 0.95 (+1.96)
     - acoustic fit (+0.03)

4. Storm Runner by Voltline
   Score: 1.97
   Reasons:
     - energy 0.91 vs target 0.95 (+1.92)
     - acoustic fit (+0.05)

5. Sunrise City by Neon Echo
   Score: 1.83
   Reasons:
     - energy 0.82 vs target 0.95 (+1.74)
     - acoustic fit (+0.09)
```

**Preference silently ignored.** There are no acoustic metal songs, and acoustic fit is worth at most 0.5, so `likes_acoustic=True` changes almost nothing (+0.01). The user gets no hint that part of their request couldn't be met.

#### Genre Not in Catalog

```
============================================================
Genre Not in Catalog: top 5 recommendations
Profile: genre='k-pop', mood='happy', energy=0.7
============================================================

1. Rooftop Lights by Indigo Parade
   Score: 2.88
   Reasons:
     - mood matches happy (+1.0)
     - energy 0.76 vs target 0.70 (+1.88)

2. Sunrise City by Neon Echo
   Score: 2.76
   Reasons:
     - mood matches happy (+1.0)
     - energy 0.82 vs target 0.70 (+1.76)

3. Night Drive Loop by Neon Echo
   Score: 1.90
   Reasons:
     - energy 0.75 vs target 0.70 (+1.90)

4. Concrete Crown by K-Verse
   Score: 1.84
   Reasons:
     - energy 0.78 vs target 0.70 (+1.84)

5. Fuego Lento by Los Caminos
   Score: 1.80
   Reasons:
     - energy 0.80 vs target 0.70 (+1.80)
```

**Degrades gracefully but silently.** "k-pop" never matches, so the system falls back to mood and energy, which is reasonable. It doesn't tell the user their genre isn't in the catalog.

#### Messy Input

```
============================================================
Messy Input: top 5 recommendations
Profile: genre=' Pop ', mood='HAPPY', energy=0.8
============================================================

1. Sunrise City by Neon Echo
   Score: 2.96
   Reasons:
     - mood matches HAPPY (+1.0)
     - energy 0.82 vs target 0.80 (+1.96)

2. Rooftop Lights by Indigo Parade
   Score: 2.92
   Reasons:
     - mood matches HAPPY (+1.0)
     - energy 0.76 vs target 0.80 (+1.92)

3. Fuego Lento by Los Caminos
   Score: 2.00
   Reasons:
     - energy 0.80 vs target 0.80 (+2.00)

4. Concrete Crown by K-Verse
   Score: 1.96
   Reasons:
     - energy 0.78 vs target 0.80 (+1.96)

5. Night Drive Loop by Neon Echo
   Score: 1.90
   Reasons:
     - energy 0.75 vs target 0.80 (+1.90)
```

**Bug: whitespace breaks matching.** `"HAPPY"` still matches (the comparison ignores capitalization), but `" Pop "` with spaces does not, because the input is never trimmed. The pop fan loses the genre bonus, and *Gym Hero* drops out of the top 5.

#### Out-of-Range Energy

```
============================================================
Out-of-Range Energy: top 5 recommendations
Profile: genre='classical', mood='peaceful', energy=1.5
============================================================

1. Moonlit Prelude by Elena Varga
   Score: 2.30
   Reasons:
     - genre matches classical (+2.0)
     - mood matches peaceful (+1.0)
     - energy 0.15 vs target 1.50 (+-0.70)

2. Iron Tempest by Graveforge
   Score: 0.94
   Reasons:
     - energy 0.97 vs target 1.50 (+0.94)

3. Neon Euphoria by Pulse District
   Score: 0.90
   Reasons:
     - energy 0.95 vs target 1.50 (+0.90)

4. Gym Hero by Max Pulse
   Score: 0.86
   Reasons:
     - energy 0.93 vs target 1.50 (+0.86)

5. Storm Runner by Voltline
   Score: 0.82
   Reasons:
     - energy 0.91 vs target 1.50 (+0.82)
```

**Bug: negative points.** Energy 1.5 is outside the 0–1 scale, so the closeness formula goes negative (`+-0.70`). *Moonlit Prelude* still wins on labels, but the input should be rejected or clamped to 0–1.

#### Empty Profile

```
============================================================
Empty Profile: top 5 recommendations
Profile: (none)
============================================================

1. Sunrise City by Neon Echo
   Score: 0.00
   Reasons:
     - no matching preferences

2. Midnight Coding by LoRoom
   Score: 0.00
   Reasons:
     - no matching preferences

3. Storm Runner by Voltline
   Score: 0.00
   Reasons:
     - no matching preferences

4. Library Rain by Paper Lanterns
   Score: 0.00
   Reasons:
     - no matching preferences

5. Gym Hero by Max Pulse
   Score: 0.00
   Reasons:
     - no matching preferences
```

**Misleading output.** Every song scores 0.00, so the "top 5" is just the first five rows of the CSV. The system presents arbitrary songs as recommendations instead of saying it needs preferences.

### Comparing profiles side by side

Each comparison changes one or two preferences and checks whether the list moves in the direction it should.

- **High-Energy Pop vs. Chill Lofi:** the two lists share **no songs at all**. The pop list is all lively songs (energy 0.76–0.93), and the lofi list is all quiet ones (0.28–0.42), led by soft, acoustic tracks like *Library Rain* and *Coffee Shop Stories*. This makes sense: the two listeners asked for opposite ends of the energy scale, and the lofi fan's "likes acoustic" setting pulls the list further toward gentle songs.

- **High-Energy Pop vs. Deep Intense Rock:** both want loud music, so they share *Gym Hero* and *Concrete Crown*. The difference is the *feel*. The rock fan also asked for darker-sounding music (valence 0.4), so their list brings in brooding songs like *Iron Tempest* and *Night Drive Loop*, while the pop list keeps bright, fun songs like *Sunrise City* and *Fuego Lento*. Same energy, different mood, and the list shifts the way it should.

- **Chill Lofi vs. Deep Intense Rock:** again no overlap. The rock fan dislikes acoustic music and the lofi fan likes it, so loud electric songs lose points twice for the lofi fan: once for energy and once for texture. That's why the two lists are so far apart.

- **Deep Intense Rock vs. Energetic but Sad:** both want energy around 0.9, and ranks 2–5 of the "sad" list (*Storm Runner*, *Gym Hero*, *Neon Euphoria*, *Iron Tempest*) are almost the same loud songs the rock fan gets. The only real difference is *Paper Hearts*, a quiet sad folk song, at #1. This shows the system only knows a song is "sad" from its mood label. It can't find songs that are loud *and* sad-sounding, so the listener gets one sad song that's too quiet and four loud songs that aren't sad. The math is working as designed, but the result isn't what a person would want.

- **Deep Intense Rock vs. Acoustic Headbanger:** the headbanger asked for acoustic metal, but their list is almost the same loud, electric songs. "Likes acoustic" added only +0.01 to +0.09 points. The catalog has no loud acoustic songs, and acoustic fit is the smallest part of the score, so this preference barely changes anything.

- **High-Energy Pop vs. Messy Input:** these are the *same* request, except the second one typed `" Pop "` with spaces. *Sunrise City* falls from 4.96 to 2.96 points, and *Gym Hero* drops out of the top 5 completely. That shouldn't happen, and it shows the genre match is fragile: the spaces stop it from counting at all.

- **High-Energy Pop vs. Genre Not in Catalog:** without a genre that matches anything, *Rooftop Lights* moves up to #1 ahead of *Sunrise City*. This makes sense: with no genre bonus for anyone, the ranking comes down to mood and energy, and this listener's target (0.7) is closer to *Rooftop Lights* (0.76) than to *Sunrise City* (0.82).

- **Chill Lofi vs. Out-of-Range Energy:** both name calm labels (classical, peaceful), but the impossible energy target of 1.5 fills the out-of-range list with the loudest songs in the catalog. *Moonlit Prelude* holds #1 only because of its labels, despite *losing* 0.70 points on energy. That isn't valid; the input should have been rejected.

- **Empty Profile vs. every other profile:** with no preferences, every song scores 0, and the "top 5" is just the first five rows of the CSV file. This shows the ranking reflects nothing but the order of the data when there's nothing to compare against.

### Why does "Gym Hero" keep showing up for someone who wants Happy Pop?

The recommender reads the **label on the box**, not what's inside. *Gym Hero* is labeled "pop," which earns the biggest single bonus (+2.0), and its energy (0.93) is close enough to the listener's 0.8 to earn most of the energy points too (+1.74). It doesn't get the "happy" point, because it's labeled "intense," but the genre bonus alone outweighs that.

*Rooftop Lights* is the more obviously happy song, but its label says "indie pop." To the computer, "indie pop" and "pop" are different words, so it gets no genre bonus at all. The result is that a workout anthem ranks above a sunny, happy song for someone who just wants happy pop.

*Gym Hero* also turns up in **6 of the 9** lists overall. It's one of the loudest, least acoustic songs in the catalog, so it scores well for *anyone* who wants high energy, whether they asked for pop, rock or something sad.

### What surprised me

- **Labels beat numbers whenever both match.** A genre + mood match (+3.0) is worth more than a perfect energy match (+2.0), so contradictory profiles get one "label" song followed by unrelated "energy" songs.
- **The system never says "I don't know."** Unknown genres, impossible combinations and empty profiles all produce confident-looking top-5 lists.
- **Input checking matters as much as the math.** Two of the failures (spaces, out-of-range energy) are about validating input, not about the scoring recipe itself.
- **A few loud songs dominate, and middle-energy songs vanish.** *Gym Hero*, *Sunrise City* and *Storm Runner* each appeared in 5–6 of the 9 lists, while *Velvet Hours*, *Dusty Backroads*, *Island Time* and *Gray Morning Blues* never made a top 5.
- **Changing the weights mostly changed *which* preference gets ignored.** When I doubled energy and halved genre (see the README's Experiments section), the Happy Pop list improved, but the "Energetic but Sad" listener lost their only sad song instead of getting a better balance.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
