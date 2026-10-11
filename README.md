# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Describe the game's purpose.** It's a number guessing game built with Streamlit. You pick a difficulty (Easy 1–20 with 6 attempts, Normal 1–100 with 8, Hard 1–200 with 5) and try to guess the secret number. After each guess you get a "Go HIGHER" or "Go LOWER" hint. You win by guessing it before you run out of attempts. Fewer guesses means a higher score.
- [x] **Detail which bugs you found.** (Full reproduction log in [reflection.md](reflection.md).)
  1. Hints were backwards. "Too High" said "Go HIGHER".
  2. On every even attempt the secret was turned into a string, so guesses were compared alphabetically (`"9" > "80"`).
  3. Out-of-range guesses like `0` and `-1` were accepted and used up attempts.
  4. Attempts started at 1, so Normal only gave 7 of its 8 guesses.
  5. "New Game" didn't reset status, score, or history (you stayed on "Game over"). It also ignored the difficulty range.
  6. The prompt always said "1 and 100", Hard (1–50) was easier than Normal, and switching difficulty kept the old secret.
  7. Scoring was inconsistent. A wrong "Too High" guess *added* points on even attempts, and the win bonus was off by one.
- [x] **Explain what fixes you applied.**
  - Moved all game logic (`get_range_for_difficulty`, `parse_guess`, `check_guess`, `update_score`, plus a new `get_hint_message`) into `logic_utils.py`. `app.py` now only handles UI and session state.
  - `check_guess` always compares ints and returns `"Win"` / `"Too High"` / `"Too Low"`. The hint text comes from `get_hint_message`, with the messages un-swapped.
  - `parse_guess(raw, low, high)` rejects out-of-range numbers, decimals like `2.5`, and junk like `abc`, `nan`, and `1e309`. Invalid input doesn't use up an attempt.
  - Added `start_new_game()` in `app.py` to reset *all* per-game state. It runs on first load, on "New Game", and whenever the difficulty changes.
  - Scoring: a first-guess win is worth 100 points, minus 10 for each extra guess (min 10). Every wrong guess costs 5.
  - The "Attempts left" box and Debug panel now render after the guess is processed, so they no longer lag one guess behind.

## 📸 Demo Walkthrough

A sample game on **Normal** (range 1–100, 8 attempts). The secret is 80 (visible in "Developer Debug Info"):

1. Game loads and shows "Guess a number between 1 and 100. Attempts left: 8". Score is 0.
2. User enters a guess of **50**. Game returns "Too Low" and shows "📈 Go HIGHER!". Attempts left: 7, score: -5.
3. User enters **0**. Game shows "Enter a number between 1 and 100." No attempt is used and the score doesn't change.
4. User enters **2.5**. Game shows "Please enter a whole number." No attempt is used.
5. User enters **90**. Game returns "Too High" and shows "📉 Go LOWER!". Attempts left: 6, score: -10.
6. User enters **85**. Game shows "📉 Go LOWER!". Attempts left: 5, score: -15.
7. User enters **80**. Game shows "🎉 Correct!", balloons, and "You won! The secret was 80. Final score: 55" (4th guess = 70 points, minus 15 for three wrong guesses).
8. Submitting again shows "You already won. Start a new game to play again."
9. Clicking **New Game 🔁** resets attempts to 8 and score to 0, clears history, and picks a new secret within the current difficulty's range.
10. Switching the sidebar to **Easy** changes the prompt to "between 1 and 20" and starts a fresh game with a secret in 1–20.

## 🧪 Test Results

Run with `python -m pytest -v` (also saved to [test_results.txt](test_results.txt)):

```
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0 -- C:\Dan\download\github\ai110-module1show-gameglitchinvestigator-starter\.venv\Scripts\python.exe
rootdir: C:\Dan\download\github\ai110-module1show-gameglitchinvestigator-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collecting ... collected 25 items

tests/test_game_logic.py::test_winning_guess PASSED                      [  4%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [  8%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 12%]
tests/test_game_logic.py::test_hint_for_too_low_says_go_higher PASSED    [ 16%]
tests/test_game_logic.py::test_hint_for_too_high_says_go_lower PASSED    [ 20%]
tests/test_game_logic.py::test_comparison_is_numeric_not_alphabetical PASSED [ 24%]
tests/test_game_logic.py::test_out_of_range_guesses_rejected PASSED      [ 28%]
tests/test_game_logic.py::test_boundary_guesses_accepted PASSED          [ 32%]
tests/test_game_logic.py::test_wrong_guess_always_costs_points PASSED    [ 36%]
tests/test_game_logic.py::test_win_on_first_guess_is_worth_100 PASSED    [ 40%]
tests/test_game_logic.py::test_hard_range_is_wider_than_normal PASSED    [ 44%]
tests/test_game_logic.py::test_negative_numbers_rejected[-5] PASSED      [ 48%]
tests/test_game_logic.py::test_negative_numbers_rejected[-1000000] PASSED [ 52%]
tests/test_game_logic.py::test_decimals[2.5-expected0] PASSED            [ 56%]
tests/test_game_logic.py::test_decimals[50.0-expected1] PASSED           [ 60%]
tests/test_game_logic.py::test_extremely_large_values_rejected_without_crashing[99999999999999999999999] PASSED [ 64%]
tests/test_game_logic.py::test_extremely_large_values_rejected_without_crashing[1e309] PASSED [ 68%]
tests/test_game_logic.py::test_extremely_large_values_rejected_without_crashing[1e5] PASSED [ 72%]
tests/test_game_logic.py::test_empty_and_non_numeric_input[] PASSED      [ 76%]
tests/test_game_logic.py::test_empty_and_non_numeric_input[   ] PASSED   [ 80%]
tests/test_game_logic.py::test_empty_and_non_numeric_input[None] PASSED  [ 84%]
tests/test_game_logic.py::test_empty_and_non_numeric_input[abc] PASSED   [ 88%]
tests/test_game_logic.py::test_empty_and_non_numeric_input[nan] PASSED   [ 92%]
tests/test_game_logic.py::test_empty_and_non_numeric_input[inf] PASSED   [ 96%]
tests/test_game_logic.py::test_whitespace_around_number_is_ignored PASSED [100%]

============================= 25 passed in 0.04s ==============================
```

The suite contains the 3 starter tests, 8 regression tests (one per fixed bug), and 14 Challenge 1 edge-case tests (negative numbers, decimals, huge values, empty or non-numeric input, whitespace). See [ai_interactions.md](ai_interactions.md).

## 🚀 Stretch Features

- [x] **Challenge 1: Advanced Edge-Case Testing.** See the edge-case section of `tests/test_game_logic.py`, the test output above, and [ai_interactions.md](ai_interactions.md).
