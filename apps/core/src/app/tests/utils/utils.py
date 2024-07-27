import random
import string


def random_lower_string(size=16) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=size))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"
