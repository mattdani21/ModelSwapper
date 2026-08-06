"""Grading helpers."""

_GRADE_LABELS = {"A": "excellent", "B": "good", "C": "fair", "D": "poor", "F": "failing"}


def _check_score(score):
    if score < 0 or score > 100:
        raise ValueError("score out of range")


def _score_to_grade(score):
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def letter_grade(score):
    _check_score(score)
    return _score_to_grade(score)


def classify(score):
    _check_score(score)
    return _GRADE_LABELS[_score_to_grade(score)]
