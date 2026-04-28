import time
from typing import Optional
import redis
from fastapi import HTTPException, Request
from app.core.config import settings

# Create Redis connection
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class RateLimiter:
    """
    Sliding window rate limiter using Redis.
    
    How it works:
    1. Each request adds a timestamp to a Redis sorted set
    2. Old timestamps (outside the window) are removed
    3. Count remaining timestamps - if over limit, reject
    """
    
    def __init__(self, requests: int, window: int, key_prefix: str):
        """
        Args:
            requests: Number of requests allowed
            window: Time window in seconds
            key_prefix: Prefix for Redis key (e.g., "upload", "ask")
        """
        self.requests = requests
        self.window = window
        self.key_prefix = key_prefix
    
    async def check_rate_limit(self, request: Request, user_id: Optional[str] = None):
        """
        Check if request should be allowed or rate limited.
        
        Args:
            request: FastAPI request object (to get IP address)
            user_id: Optional user ID (if authenticated)
        
        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        # Create unique key for this user/IP
        identifier = user_id if user_id else request.client.host
        redis_key = f"rate_limit:{self.key_prefix}:{identifier}"
        
        # Current timestamp
        now = time.time()
        
        # Window start time (e.g., 60 seconds ago)
        window_start = now - self.window
        
        # Remove old entries outside the window
        redis_client.zremrangebyscore(redis_key, 0, window_start)
        
        # Count requests in current window
        request_count = redis_client.zcard(redis_key)
        
        # Check if limit exceeded
        if request_count >= self.requests:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": self.requests,
                    "window": f"{self.window} seconds",
                    "retry_after": int(self.window)
                }
            )
        
        # Add current request to the sorted set
        redis_client.zadd(redis_key, {str(now): now})
        
        # Set expiration on the key (cleanup)
        redis_client.expire(redis_key, self.window)
        
        # Return remaining requests (useful for headers)
        return {
            "limit": self.requests,
            "remaining": self.requests - request_count - 1,
            "reset": int(now + self.window)
        }


# Pre-configured rate limiters for different endpoints
upload_limiter = RateLimiter(requests=5, window=3600, key_prefix="upload")  # 5 per hour
ask_limiter = RateLimiter(requests=20, window=60, key_prefix="ask")  # 20 per minute
docs_limiter = RateLimiter(requests=100, window=60, key_prefix="docs")  # 100 per minute
auth_limiter = RateLimiter(requests=5, window=900, key_prefix="auth")  # 5 per 15 min
