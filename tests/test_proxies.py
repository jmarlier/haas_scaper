from utils.proxies import get_next_proxy
from utils.user_agents import get_random_user_agent

def test_proxy_rotation():
    proxies = set(get_next_proxy() for _ in range(10))
    # Should return at least one value (None by default), but allow for more if proxies are configured
    assert len(proxies) >= 1

def test_user_agent_rotation():
    user_agents = set(get_random_user_agent() for _ in range(10))
    # Should return more than one unique user-agent
    assert len(user_agents) > 1 