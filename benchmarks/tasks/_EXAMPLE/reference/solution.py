def most_common_word(text):
    """Return the most frequent word, ignoring case and punctuation.

    Ties are broken by first occurrence. Returns None for empty input.
    """
    if not text:
        return None
    words = []
    for w in text.lower().split():
        words.append(w.strip(".,!?;:\"'()[]{}"))
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    best = None
    best_count = 0
    for w in words:
        if counts[w] > best_count:  # strict > keeps first occurrence on ties
            best = w
            best_count = counts[w]
    return best
