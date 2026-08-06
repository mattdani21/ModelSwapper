def reverse_words(sentence):
    """Return the words of sentence in reverse order, joined by single
    spaces. Whitespace-only or empty input yields an empty string.
    """
    return " ".join(sentence.split()[::-1])
