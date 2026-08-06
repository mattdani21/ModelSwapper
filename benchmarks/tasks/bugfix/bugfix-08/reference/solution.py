def parse_csv(text):
    """Parse a CSV string into a list of rows of field strings."""
    if not text:
        return []
    rows = []
    for line in text.strip().split("\n"):
        fields = []
        current = []
        in_quotes = False
        i = 0
        while i < len(line):
            c = line[i]
            if c == '"' and (not current or in_quotes):
                if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                    current.append('"')
                    i += 1
                else:
                    in_quotes = not in_quotes
            elif c == "," and not in_quotes:
                fields.append("".join(current))
                current = []
            else:
                current.append(c)
            i += 1
        fields.append("".join(current))
        rows.append(fields)
    return rows
