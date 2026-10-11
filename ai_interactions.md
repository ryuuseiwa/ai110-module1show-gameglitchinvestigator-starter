# AI Interactions Log

> **Stretch features only.** This file documents **Challenge 1: Advanced Edge-Case Testing**. Sections for stretch features I did not attempt were removed.

---

## Test Generation (SF7)

**Prompts used (Claude Code in VS Code):**

```
1. "Now that parse_guess checks the range, what three kinds of 'edge case' input could
   still break the game? Think negative numbers, decimals, and extremely large values."

2. "Generate a pytest suite in tests/test_game_logic.py that verifies parse_guess handles
   those inputs gracefully: it should return (False, None, <message>) instead of crashing
   or silently accepting a bad value. Use parametrize where it keeps things short."
```

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Negative numbers (`-5`, `-1000000`) | Prompt 1 + 2 | `test_negative_numbers_rejected` (parametrized): `parse_guess(raw, 1, 100)` returns `ok=False` | ✅ Yes | This is the exact bug I hit while playing (0 and -1 were accepted), so it should never come back. |
| Decimals (`2.5`, `50.0`) | Prompt 1 + 2 | `test_decimals`: `2.5` returns "Please enter a whole number.", `50.0` returns `(True, 50, None)` | ✅ Yes | The original code silently cut `2.5` down to `2`, so the player guessed a number they never typed. `50.0` is still a whole number, so I accept it. |
| Extremely large values (`99999999999999999999999`, `1e309`, `1e5`) | Prompt 1 + 2 | `test_extremely_large_values_rejected_without_crashing` | ✅ Yes | `float("1e309")` is infinity, and `int(inf)` raises `OverflowError`. The old code only worked because of a bare `except Exception`. Now that error is caught on purpose, and huge numbers fail the range check. |
| Empty / non-numeric (`""`, `"   "`, `None`, `abc`, `nan`, `inf`) | Prompt 2 (follow-up) | `test_empty_and_non_numeric_input` | ✅ Yes | Whitespace-only input and `nan`/`inf` are sneaky inputs. They need a friendly message, not a crash. |
| Whitespace around a number (`"  42 "`) | Prompt 2 (follow-up) | `test_whitespace_around_number_is_ignored` | ✅ Yes | It's easy to type a stray space by accident, and that shouldn't make a valid guess count as invalid. |

**Result:** all 25 tests pass. See the fenced pytest output in [README.md](README.md) and [test_results.txt](test_results.txt).
