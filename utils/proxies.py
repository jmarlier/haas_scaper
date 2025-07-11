import random

PROXIES = [
    None,  # no proxy
    # "http://user:pass@proxy1.example.com:3128",
    # "http://user:pass@proxy2.example.com:3128",
    # Add valid proxies here if you have any
]

def get_next_proxy() -> str | None:
    return random.choice(PROXIES)