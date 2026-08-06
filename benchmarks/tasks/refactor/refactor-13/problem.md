# Task: extract duplicated text normalization

`solution.py` analyzes text. `top_words(text, n)` and
`keyword_counts(text, keywords)` both inline the same two steps: normalize the
text into lowercase word tokens (matching the existing `[a-z0-9']+` pattern)
and tally word counts with a dict.

Refactor the module so that:

- Add a helper `_normalize(text)` that returns the list of word tokens for
  the lowercased text. The tokenization must appear exactly once, inside this
  helper.
- Add a helper `_tally(words)` that returns a dict mapping each word to its
  count. The counting must appear exactly once, inside this helper.
- `top_words(text, n)` keeps its signature and behavior (most frequent words,
  ties broken alphabetically, at most `n` results) and must delegate to the
  helpers.
- `keyword_counts(text, keywords)` keeps its signature and behavior (a count
  for each keyword, 0 for keywords that do not occur) and must delegate to
  the helpers.

Do not change behavior. Stdlib only.
