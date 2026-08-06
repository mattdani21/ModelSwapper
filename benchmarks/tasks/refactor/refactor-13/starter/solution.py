"""Text analysis helpers."""

import re

_WORD_RE = re.compile(r"[a-z0-9']+")


def top_words(text, n):
    words = [m.group(0) for m in _WORD_RE.finditer(text.lower())]
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [w for w, _ in ranked[:n]]


def keyword_counts(text, keywords):
    words = [m.group(0) for m in _WORD_RE.finditer(text.lower())]
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    return {k: counts.get(k, 0) for k in keywords}
