"""Grading helpers."""


def letter_grade(score):
    if score < 0 or score > 100:
        raise ValueError("score out of range")
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def classify(score):
    if score < 0 or score > 100:
        raise ValueError("score out of range")
    if score >= 90:
        return "excellent"
    if score >= 80:
        return "good"
    if score >= 70:
        return "fair"
    if score >= 60:
        return "poor"
    return "failing"
