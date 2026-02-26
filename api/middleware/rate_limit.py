"""
Rate Limiting Middleware for FastAPI
=====================================

Simple in-memory rate limiting to prevent API abuse.

Features:
    - Tracks requests per IP address
    - Configurable requests per minute threshold
    - Automatic cleanup of old requests
    - Returns 429 Too Many Requests on rate limit

Usage:
    app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware
    
    Tracks requests per client IP and enforces rate limits.
    """
    
    def __init__(self, app, requests_per_minute: int = 100):
        """
        Initialize rate limiter
        
        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests allowed per minute per IP
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.client_requests: Dict[str, List[datetime]] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler
        
        Returns:
            Response or raises HTTPException if rate limit exceeded
        """
        # Get client IP
        client_ip = request.client.host
        
        # Clean old requests (older than 1 minute)
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        self.client_requests[client_ip] = [
            req_time for req_time in self.client_requests[client_ip]
            if req_time > cutoff
        ]
        
        # Check rate limit
        if len(self.client_requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute."
            )
        
        # Record request
        self.client_requests[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.client_requests[client_ip])
        )
        
        return response
