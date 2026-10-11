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

I used **Claude Code** (the Claude extension in VS Code) as my AI teammate. I described what I saw while playing (50 → "Go LOWER" when the secret was 80, and 0 and -1 being accepted). Then I had it trace the code, mark the FIXME locations, refactor the logic into `logic_utils.py`, and write pytest cases.

**A suggestion that was correct:** Claude explained that "Go LOWER" for a guess of 50 had *two* causes stacked together. The messages in `check_guess` were swapped. Also, on even attempts `app.py` turned the secret into a string, so `50 > "80"` raised a `TypeError` that was caught silently, and the fallback compared `"50"` and `"80"` alphabetically. It suggested deleting the `str(secret)` branch and the `except TypeError` fallback completely, so `check_guess` only ever compares ints, instead of trying to patch the fallback. That was right because the fallback only existed to hide the type mix-up. I verified it with `test_comparison_is_numeric_not_alphabetical` (`check_guess(9, 80)` is now "Too Low", where the string version said "Too High"). I also replayed my original game, and with the secret at 80, guessing 50 now says "Go HIGHER".

**A suggestion I did not accept as written:** The original AI-written code had `check_guess` return a tuple `(outcome, message)`, and the simple "move it to logic_utils.py and update the import" refactor would have kept it that way. But the starter tests call `check_guess(50, 50)` and expect `"Win"`, a plain string. So the tuple design would mean rewriting the starter tests to fit the code. Instead I changed the design. `check_guess` now returns just the outcome, and a small separate `get_hint_message(outcome)` returns the emoji text from one dictionary. That kept the existing tests valid, kept the logic easy to test, and put the swapped-message fix in one easy-to-read place. I verified it by running `pytest`: the 3 original starter tests pass unchanged alongside the new ones, and the hint text in the live game is correct.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

I only counted a bug as fixed when two things were true: a pytest test that targets it passes, *and* the original reproduction from my bug log behaves correctly in the game. For example, `test_out_of_range_guesses_rejected` checks that `parse_guess("0", 1, 100)` and `parse_guess("-1", 1, 100)` return `ok=False` with "Enter a number between 1 and 100". In the game, typing 0 now shows that error and "Attempts left" stays the same, where before it went down. `test_wrong_guess_always_costs_points` loops over attempts 1–8 and showed that the old even-attempt "+5" for a wrong guess is gone. I also replayed a full game with Streamlit's `AppTest` (guesses 50, 0, -1, 20, 90, 2.5, 85, 80 against secret 80). It confirmed the hints were right, invalid input didn't use up attempts, the final score was 40, New Game works after both a win and a loss, and switching to Easy changes the prompt to 1–20. Claude helped design the edge-case tests by listing inputs that might still break `parse_guess`, like `1e309` (which turns into infinity and makes `int()` raise `OverflowError`), `nan`, and `2.5` (which used to be silently cut down to 2). The final run is 25 passed (see `test_results.txt` and the README).

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

Streamlit reruns your whole Python script from top to bottom every time you click a button or type something. So any normal variable, like `secret = random.randint(...)`, gets recreated on every click. `st.session_state` is a dictionary that survives those reruns, which is why the secret, attempts, score, and history have to live there and only get set when a new game starts. Order matters too. Because the script runs top to bottom, the original "Attempts left" box and Debug panel were drawn *before* the guess was processed, so they always showed the previous turn's numbers. I fixed that with an `st.empty()` placeholder that gets filled in at the end. The "New Game" bug was also about state: resetting only a couple of keys left the old `status = "lost"` in session state, so the game stayed stuck on "Game over".

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.

**One habit I want to reuse:** writing a bug reproduction table (input → expected → actual → code location) *before* fixing anything, then turning each row into a pytest test. It made it obvious when something was really fixed, and the tests will catch it if the bug comes back. I'll also keep committing after each phase instead of one big commit at the end.

**What I'd do differently:** I'd check the AI's assumptions against the existing tests earlier. The tuple-vs-string mismatch between the original `check_guess` and the starter tests was a clue I could have caught in the first five minutes. I'd also ask the AI to explain *why* a line exists before accepting a fix, like the `except TypeError` fallback that was only covering up the real bug.

**How this changed my view of AI-generated code:** Code that looks clean and runs without errors can still be completely wrong. This game never crashed, but its hints lied, and the AI-written `try/except` made sure the type bug never showed up. Now I treat AI code as a first draft that I have to verify with tests and by actually playing it, not as something that's production-ready because it says so.
