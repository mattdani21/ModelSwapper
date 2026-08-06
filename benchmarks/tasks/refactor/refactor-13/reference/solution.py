"""Text analysis helpers."""

import re

_WORD_RE = re.compile(r"[a-z0-9']+")


def _normalize(text):
    return [m.group(0) for m in _WORD_RE.finditer(text.lower())]


def _tally(words):
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    return counts


def top_words(text, n):
    ranked = sorted(_tally(_normalize(text)).items(), key=lambda kv: (-kv[1], kv[0]))
    return [w for w, _ in ranked[:n]]


def keyword_counts(text, keywords):
    counts = _tally(_normalize(text))
    return {k: counts.get(k, 0) for k in keywords}
