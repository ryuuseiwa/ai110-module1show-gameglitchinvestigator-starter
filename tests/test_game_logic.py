from logic_utils import check_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# --- Regression tests for the bugs fixed in Phase 2 ---
# FIX: Generated with Claude Code, one test per bug from the reproduction log in reflection.md.

import pytest

from logic_utils import get_hint_message, get_range_for_difficulty, parse_guess, update_score


def test_hint_for_too_low_says_go_higher():
    # Bug: secret 80, guess 50 showed "Go LOWER"
    outcome = check_guess(50, 80)
    assert outcome == "Too Low"
    assert "HIGHER" in get_hint_message(outcome)


def test_hint_for_too_high_says_go_lower():
    outcome = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in get_hint_message(outcome)


def test_comparison_is_numeric_not_alphabetical():
    # Bug: as strings, "9" > "80" and "2" < "80" is only right by luck
    assert check_guess(9, 80) == "Too Low"
    assert check_guess(100, 80) == "Too High"


def test_out_of_range_guesses_rejected():
    # Bug: 0 and -1 were accepted on a 1-100 game
    for raw in ["0", "-1", "101"]:
        ok, value, err = parse_guess(raw, 1, 100)
        assert not ok
        assert value is None
        assert "between 1 and 100" in err


def test_boundary_guesses_accepted():
    assert parse_guess("1", 1, 100) == (True, 1, None)
    assert parse_guess("100", 1, 100) == (True, 100, None)


def test_wrong_guess_always_costs_points():
    # Bug: "Too High" on an even attempt added 5 points
    for attempt in range(1, 9):
        assert update_score(0, "Too High", attempt) == -5
        assert update_score(0, "Too Low", attempt) == -5


def test_win_on_first_guess_is_worth_100():
    # Bug: win bonus used attempt_number + 1 (off by one)
    assert update_score(0, "Win", 1) == 100
    assert update_score(0, "Win", 2) == 90
    assert update_score(0, "Win", 20) == 10  # floor


def test_hard_range_is_wider_than_normal():
    # Bug: Hard was 1-50, easier than Normal's 1-100
    easy, normal, hard = (get_range_for_difficulty(d) for d in ("Easy", "Normal", "Hard"))
    assert easy[1] < normal[1] < hard[1]


# --- Challenge 1: edge-case inputs ---

@pytest.mark.parametrize("raw", ["-5", "-1000000"])
def test_negative_numbers_rejected(raw):
    ok, value, _ = parse_guess(raw, 1, 100)
    assert not ok and value is None


@pytest.mark.parametrize("raw, expected", [("2.5", (False, None, "Please enter a whole number.")),
                                           ("50.0", (True, 50, None))])
def test_decimals(raw, expected):
    assert parse_guess(raw, 1, 100) == expected


@pytest.mark.parametrize("raw", ["99999999999999999999999", "1e309", "1e5"])
def test_extremely_large_values_rejected_without_crashing(raw):
    ok, value, err = parse_guess(raw, 1, 100)
    assert not ok and value is None and err


@pytest.mark.parametrize("raw", ["", "   ", None, "abc", "nan", "inf"])
def test_empty_and_non_numeric_input(raw):
    ok, value, err = parse_guess(raw, 1, 100)
    assert not ok and value is None and err


def test_whitespace_around_number_is_ignored():
    assert parse_guess("  42 ", 1, 100) == (True, 42, None)
