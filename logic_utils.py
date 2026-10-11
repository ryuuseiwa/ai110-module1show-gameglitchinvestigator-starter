"""Core game logic for the number guessing game, kept free of Streamlit so it can be tested."""

# FIX: Refactored all game logic out of app.py into this module using Claude Code (agent mode),
# so pytest can exercise it without starting the Streamlit UI.

DIFFICULTY_RANGES = {
    "Easy": (1, 20),
    "Normal": (1, 100),
    # FIX: Hard used to be 1-50, which was *easier* than Normal. Widened to 1-200.
    "Hard": (1, 200),
}

HINT_MESSAGES = {
    "Win": "🎉 Correct!",
    # FIX: These two messages were swapped. Too High now tells you to go lower.
    "Too High": "📉 Go LOWER!",
    "Too Low": "📈 Go HIGHER!",
}


def get_range_for_difficulty(difficulty: str):
    """Return the inclusive (low, high) range for a difficulty.

    Args:
        difficulty: One of "Easy", "Normal", or "Hard".

    Returns:
        A (low, high) tuple. Unknown difficulties fall back to the Normal range.
    """
    return DIFFICULTY_RANGES.get(difficulty, DIFFICULTY_RANGES["Normal"])


def parse_guess(raw: str, low: int = None, high: int = None):
    """Parse user input into an int guess, optionally enforcing a range.

    Args:
        raw: The raw text the user typed.
        low: Smallest allowed guess (inclusive), or None for no lower bound.
        high: Largest allowed guess (inclusive), or None for no upper bound.

    Returns:
        (ok, guess_int, error_message). When ok is False, guess_int is None.
    """
    if raw is None or raw.strip() == "":
        return False, None, "Enter a guess."

    text = raw.strip()
    try:
        if "." in text or "e" in text.lower():
            number = float(text)
            # FIX: "2.5" used to be silently truncated to 2. Only whole numbers count now.
            if not number.is_integer():
                return False, None, "Please enter a whole number."
            value = int(number)
        else:
            value = int(text)
    except (ValueError, OverflowError):
        return False, None, "That is not a number."

    # FIX: There was no range check, so 0 and -1 were accepted as real guesses.
    if (low is not None and value < low) or (high is not None and value > high):
        return False, None, f"Enter a number between {low} and {high}."

    return True, value, None


def check_guess(guess: int, secret: int) -> str:
    """Compare a guess to the secret.

    Args:
        guess: The player's guess.
        secret: The secret number. Both values must be ints.

    Returns:
        "Win", "Too High", or "Too Low".
    """
    # FIX: The old version caught a TypeError and fell back to *string* comparison
    # (app.py turned the secret into a str on even attempts). Both sides are ints now.
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def get_hint_message(outcome: str) -> str:
    """Return the hint text shown to the player for an outcome."""
    return HINT_MESSAGES[outcome]


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Return the new score after a guess.

    Args:
        current_score: Score before this guess.
        outcome: "Win", "Too High", or "Too Low".
        attempt_number: 1-based number of this guess (1 = first guess).

    Returns:
        A win on guess 1 is worth 100, each later guess is worth 10 less (min 10).
        Every wrong guess costs 5 points.
    """
    if outcome == "Win":
        # FIX: Was 100 - 10 * (attempt_number + 1), which was off by one.
        return current_score + max(10, 100 - 10 * (attempt_number - 1))

    # FIX: "Too High" used to *add* 5 points on even attempts. Wrong guesses now always cost 5.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
