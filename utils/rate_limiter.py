import time

# Store access times by IP address
RATE_LIMIT_STORAGE = {}
MAX_REQUESTS = 5
WINDOW_SECONDS = 10

def is_rate_limited(ip_address):
    """
    In-memory rate limiter. Allows MAX_REQUESTS per IP per WINDOW_SECONDS.

    Args:
        ip_address (str): The client's IP address.

    Returns:
        bool: True if rate limit exceeded, False otherwise.
    """
    now = time.time()
    window = RATE_LIMIT_STORAGE.get(ip_address, [])

    # Remove old timestamps
    window = [ts for ts in window if now - ts < WINDOW_SECONDS]

    if len(window) >= MAX_REQUESTS:
        return True

    # Track current request
    window.append(now)
    RATE_LIMIT_STORAGE[ip_address] = window
    return False
