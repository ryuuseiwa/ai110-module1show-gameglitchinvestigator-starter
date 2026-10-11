# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

The first time I ran it, the game looked finished: a title, a difficulty picker in the sidebar, a guess box, and a "Developer Debug Info" panel that shows the secret. It only fell apart once I played. On Normal (1 to 100) the secret was 80. I guessed 50 and it told me "Go LOWER", so I went 20, 10, 1, 0, and even -1, and every time it said "Go LOWER". It also took 0 and -1 even though it says to guess between 1 and 100. On my 7th guess (2) it said "Out of attempts! The secret was 80. Score: -35". Sidebar says 8 attempts are allowed, but I only got 7.

Concrete bugs I noticed:

1. **The hints are backwards.** When the guess is too high the game says "Go HIGHER", and when it's too low it says "Go LOWER" (`check_guess` in `app.py`).
2. **The secret flips between a number and a string.** On every even attempt the code does `secret = str(st.session_state.secret)`. Comparing `50 > "80"` throws a `TypeError`, and the fallback compares them as strings instead, which is alphabetical. So "9" > "80" but "50" < "80", and the hints don't make sense from one turn to the next (`app.py`, the submit block).
3. **Out-of-range guesses are accepted.** 0 and -1 count as real guesses and use up attempts (`parse_guess` has no range check).
4. **Off-by-one on attempts.** `attempts` starts at 1, so Normal only gives 7 guesses instead of 8. "New Game" resets it to 0, so the next game gets a different number of guesses.
5. **"New Game" doesn't really restart.** It never resets `status`, `score`, or `history`. After you win or lose, clicking New Game still says "Game over". It also always picks a secret from 1 to 100, even on Easy.
6. **Difficulty is only half wired up.** The info box always says "between 1 and 100", Hard (1 to 50) is an easier range than Normal (1 to 100), and switching difficulty keeps the old secret.
7. **Scoring is inconsistent.** A "Too High" guess on an even attempt *adds* 5 points, and the win bonus uses `attempt_number + 1`, so it's off by one.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error | Suspected Code Location |
|-------|-------------------|-----------------|------------------------|-------------------------|
| Normal, secret 80, guess `50` | "Too Low" → hint "Go HIGHER" | Hint says "📉 Go LOWER!" | none (TypeError is caught silently inside `check_guess`) | `app.py` `check_guess` (swapped messages) + submit block `str(secret)` on even attempts |
| Normal, secret 80, guess `2` (even attempt) | "Too Low" | "Too Low" only by accident: string compare `"2" < "80"`. A guess of `9` gives "Too High", which is wrong | none | `app.py` submit block: `if st.session_state.attempts % 2 == 0: secret = str(...)` |
| Normal, guesses `0` then `-1` | "Enter a number between 1 and 100", no attempt used | Both accepted as guesses, attempts used up, -5 score each | none | `app.py` `parse_guess` (no bounds check) |
| Normal, fresh game, read "Attempts left" | 8 attempts left (sidebar says 8 allowed) | Shows 7. Game ends after the 7th guess | none | `app.py` `st.session_state.attempts = 1` initializer |
| Lose a game, then click "New Game 🔁" | Fresh game starts | Still shows "Game over. Start a new game to try again." | none | `app.py` `if new_game:` block (doesn't reset `status`) |
| Switch difficulty to Easy | Prompt says 1 to 20 and secret is within 1 to 20 | Prompt still says 1 to 100. Secret stays at the old value (e.g. 80) | none | `app.py` `st.info(...)` hardcoded text. Secret is only created once |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
