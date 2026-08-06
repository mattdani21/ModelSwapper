def is_palindrome(text):
    """Return True if text is a palindrome when only letters and digits
    are considered, ignoring case and all other characters.

    Empty and whitespace-only strings count as palindromes.
    """
    cleaned = "".join(ch for ch in text if ch.isalnum()).lower()
    return cleaned == cleaned[::-1]
