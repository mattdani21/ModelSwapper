def parse_csv_line(line):
    """Parse a single CSV line into a list of fields.

    Supports double-quoted fields, escaped quotes ("" inside quotes),
    and whitespace trimming around unquoted fields.
    """
    fields = []
    buf = []
    i = 0
    n = len(line)
    in_quotes = False
    quoted = False
    while i < n:
        ch = line[i]
        if in_quotes:
            if ch == '"':
                if i + 1 < n and line[i + 1] == '"':
                    buf.append('"')
                    i += 2
                    continue
                in_quotes = False
            else:
                buf.append(ch)
        else:
            if ch == '"':
                in_quotes = True
                quoted = True
            elif ch == ',':
                fields.append("".join(buf).strip() if not quoted else "".join(buf))
                buf = []
                quoted = False
            else:
                buf.append(ch)
        i += 1
    fields.append("".join(buf).strip() if not quoted else "".join(buf))
    return fields
