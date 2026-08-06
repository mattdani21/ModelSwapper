# Task: camel_to_snake

Implement `camel_to_snake(name)` in `solution.py`.

Convert a camelCase or PascalCase identifier to snake_case:

- Insert an underscore before an uppercase letter that follows a lowercase letter or digit.
- Insert an underscore between an uppercase run and a following uppercase-then-lowercase sequence (acronyms).
- The result is fully lowercased.

Input consists of letters and digits only (may start with upper- or lowercase). Raise `ValueError` if `name` is empty.

Examples:

- `camel_to_snake("camelCase")` -> `"camel_case"`
- `camel_to_snake("PascalCase")` -> `"pascal_case"`
- `camel_to_snake("HTTPResponse")` -> `"http_response"`
- `camel_to_snake("getHTTPResponseCode")` -> `"get_http_response_code"`
- `camel_to_snake("simple")` -> `"simple"`
- `camel_to_snake("XMLParser")` -> `"xml_parser"`
- `camel_to_snake("version2Value")` -> `"version2_value"`
- `camel_to_snake("ABC")` -> `"abc"`
- `camel_to_snake("A")` -> `"a"`
- `camel_to_snake("")` raises `ValueError`

Edge cases:

- Single letters and all-caps words just get lowercased.
- Digits do not trigger underscores: `"v2"` -> `"v2"`, but `"v2X"` -> `"v2_x"`.
- Acronyms followed by a word get a separating underscore.

Do not change the function signature. Do not add prints.
