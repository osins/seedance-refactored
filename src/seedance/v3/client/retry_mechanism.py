"""Retry mechanism and exponential backoff implementation"""

import time
import random
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_retry_strategy():
    """Create a retry strategy with specific configurations."""
    return Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],  # Status codes to retry
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]  # Methods to retry
    )


def exponential_backoff_delay(attempt: int, backoff_factor: float = 1.0) -> float:
    """
    Calculate delay for exponential backoff.
    
    Args:
        attempt: Current attempt number (0-indexed)
        backoff_factor: Factor to multiply the exponential delay
        
    Returns:
        Delay in seconds
    """
    delay = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
    return delay


def apply_retry_to_session(session, retry_strategy=None):
    """
    Apply retry strategy to a requests session.
    
    Args:
        session: requests.Session object
        retry_strategy: Retry strategy to apply; if None, creates default strategy
    """
    if retry_strategy is None:
        retry_strategy = create_retry_strategy()
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)