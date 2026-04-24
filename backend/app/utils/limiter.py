"""Rate limiter for API requests"""
import time
from collections import defaultdict
from fastapi import HTTPException, status


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    def check(self, key: str):
        """Check if request is allowed"""
        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if t > minute_ago]

        if len(self.requests[key]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )

        self.requests[key].append(now)

    def reset(self, key: str):
        """Reset rate limit for a key"""
        if key in self.requests:
            del self.requests[key]


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=100)