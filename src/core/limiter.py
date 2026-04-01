from slowapi import Limiter
from slowapi.util import get_remote_address
import os

# Disable rate limiting during tests
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
    enabled=os.getenv("TESTING") != "true",
)
