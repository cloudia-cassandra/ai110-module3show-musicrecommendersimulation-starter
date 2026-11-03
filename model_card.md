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

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

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
