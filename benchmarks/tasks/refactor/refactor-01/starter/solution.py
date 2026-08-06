"""User management helpers."""


def register_user(name, email):
    name = name.strip()
    if not name or len(name) < 3 or not name.replace(" ", "").isalnum():
        raise ValueError("invalid username")
    email = email.strip().lower()
    if "@" not in email or email.count("@") != 1 or not email.split("@")[1]:
        raise ValueError("invalid email")
    return {"action": "register", "username": name, "email": email}


def login_user(name, email):
    name = name.strip()
    if not name or len(name) < 3 or not name.replace(" ", "").isalnum():
        raise ValueError("invalid username")
    email = email.strip().lower()
    if "@" not in email or email.count("@") != 1 or not email.split("@")[1]:
        raise ValueError("invalid email")
    return {"action": "login", "username": name, "email": email}
