"""Decorators for client functionality"""

import time
import random
import logging
from functools import wraps
from requests.exceptions import RequestException
from typing import List
from ..model.response_body import SeedanceResponseBody
from ..utils.retry_utils import retry_on_failure


def log_api_call(func):
    """
    Decorator to log API calls with timing information.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(__name__)
        
        # Log the API call
        start_time = time.time()
        
        # Try to extract prompt from arguments for logging
        prompt = "Unknown"
        for arg in args:
            if hasattr(arg, 'prompt'):
                prompt = getattr(arg, 'prompt', 'Unknown')[:50]
                if len(getattr(arg, 'prompt', '')) > 50:
                    prompt += '...'
                break
        
        logger.info(f"Making API call with prompt: {prompt}")

        result = func(*args, **kwargs)

        duration = time.time() - start_time
        logger.info(f"API call completed in {duration:.2f}s")

        return result
    return wrapper


def validate_input_types(expected_types: dict):
    """
    Decorator to validate input types for API calls.
    
    Args:
        expected_types: Dictionary mapping parameter names to expected types
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature to map positional args to parameter names
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate each expected type
            for param_name, expected_type in expected_types.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if value is not None and not isinstance(value, expected_type):
                        raise TypeError(f"Parameter '{param_name}' must be of type {expected_type}, got {type(value)}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def add_timeout(timeout_seconds: int):
    """
    Decorator to add timeout functionality to API calls.
    
    Args:
        timeout_seconds: Number of seconds before timeout
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This decorator would typically wrap the actual request call
            # For now, we'll just pass through to the original function
            # since timeout handling is usually done at the request level
            return func(*args, **kwargs)
        return wrapper
    return decorator


def cache_result(cache_condition_func):
    """
    Decorator to conditionally cache results based on a condition function.
    
    Args:
        cache_condition_func: Function that determines if result should be cached
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would implement caching logic
            # For now, just pass through to original function
            return func(*args, **kwargs)
        return wrapper
    return decorator


def retry_with_backoff(max_retries=3, backoff_factor=1.0, status_codes=None):
    """
    Convenience decorator that combines retry and backoff functionality.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Factor for exponential backoff
        status_codes: HTTP status codes that should trigger a retry
    """
    if status_codes is None:
        status_codes = [502, 503, 504]
    
    # Use the retry_on_failure decorator from utils
    return retry_on_failure(max_retries, backoff_factor, status_codes)