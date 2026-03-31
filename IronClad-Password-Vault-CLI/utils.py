import string
import secrets


def get_character_pool(use_upper, use_lower, use_digits, use_symbols):
    pool = ""
    if use_upper:
        pool += string.ascii_uppercase
    if use_lower:
        pool += string.ascii_lowercase
    if use_digits:
        pool += string.digits
    if use_symbols:
        pool += string.punctuation

    return pool


def generate_password(length, use_upper, use_lower, use_digits, use_symbols):
    pool = get_character_pool(use_upper, use_lower, use_digits, use_symbols)

    if not pool:
        raise ValueError("❌ You must select at least one character set.")

    password = []

    # 🔑 Ensure "at least one" rule
    if use_upper:
        password.append(secrets.choice(string.ascii_uppercase))
    if use_lower:
        password.append(secrets.choice(string.ascii_lowercase))
    if use_digits:
        password.append(secrets.choice(string.digits))
    if use_symbols:
        password.append(secrets.choice(string.punctuation))

    # Fill remaining length
    while len(password) < length:
        password.append(secrets.choice(pool))

    # Shuffle securely
    secrets.SystemRandom().shuffle(password)

    return "".join(password)


def password_strength(password):
    length = len(password)

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)

    score = sum([has_upper, has_lower, has_digit, has_symbol])

    if length >= 12 and score == 4:
        return "🟢 Strong"
    elif length >= 8 and score >= 3:
        return "🟡 Medium"
    else:
        return "🔴 Weak"