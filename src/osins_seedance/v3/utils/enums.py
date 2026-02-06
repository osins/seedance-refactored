"""Enumeration of different API error types"""

from enum import Enum


class APIErrorType(Enum):
    """Enumeration of different API error types"""
    AUTHENTICATION_ERROR = "authentication_error"
    VALIDATION_ERROR = "validation_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    SERVER_ERROR = "server_error"
    NETWORK_ERROR = "network_error"