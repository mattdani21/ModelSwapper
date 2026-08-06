def count_vowels(s):
    """Return the number of vowels (a, e, i, o, u) in s, case-insensitively."""
    count = 0
    for c in s:
        if c.lower() in "aeiou":
            count += 1
    return count
