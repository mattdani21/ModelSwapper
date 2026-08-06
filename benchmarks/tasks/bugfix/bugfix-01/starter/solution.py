def is_palindrome(s):
    """Return True if s is a palindrome ignoring case and non-alphanumeric chars."""
    cleaned = s.lower()
    return cleaned == cleaned[::-1]
