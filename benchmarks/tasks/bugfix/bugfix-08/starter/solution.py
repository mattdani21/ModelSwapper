def parse_csv(text):
    """Parse a CSV string into a list of rows of field strings."""
    if not text:
        return []
    rows = []
    for line in text.strip().split("\n"):
        fields = []
        current = []
        in_quotes = False
        for c in line:
            if c == '"':
                in_quotes = not in_quotes
            elif c == "," and not in_quotes:
                fields.append("".join(current))
                current = []
            else:
                current.append(c)
        fields.append("".join(current))
        rows.append(fields)
    return rows
