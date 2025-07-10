import random

PROXIES = [
    None,  # pas de proxy
    # "http://user:pass@proxy1.example.com:3128",
    # "http://user:pass@proxy2.example.com:3128",
    # Ajoute ici des proxies valides si tu en as
]

def get_next_proxy() -> str | None:
    return random.choice(PROXIES)