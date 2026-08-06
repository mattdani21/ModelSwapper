# Task: camel_to_snake

Implement `camel_to_snake(s)` in `solution.py`.

Convert a `camelCase` or `PascalCase` identifier to `snake_case`. Insert an
underscore before each uppercase letter that begins a new word: an uppercase
letter begins a new word when it is preceded by a lowercase letter, or when
it is followed by a lowercase letter (so acronyms such as `HTTP` form their
own word). All letters are lowercased in the output. The input contains only
ASCII letters.

Examples:

- `camel_to_snake("camelCase")` -> `"camel_case"`
- `camel_to_snake("PascalCase")` -> `"pascal_case"`
- `camel_to_snake("HTTPServer")` -> `"http_server"`
- `camel_to_snake("XMLParser")` -> `"xml_parser"`
- `camel_to_snake("simple")` -> `"simple"`
- `camel_to_snake("ABC")` -> `"abc"`

Do not change the function signature. Do not add prints.
