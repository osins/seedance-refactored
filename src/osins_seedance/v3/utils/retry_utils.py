"""Retry utilities for API requests"""

import time
import random
import logging
from functools import wraps
from requests.exceptions import RequestException
from typing import List
from ..model.response_body import SeedanceResponseBody


def retry_on_failure(max_retries=3, backoff_factor=1.0, status_codes=None):
    """
    Decorator to implement retry logic with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Factor for exponential backoff
        status_codes: HTTP status codes that should trigger a retry
    """
    if status_codes is None:
        status_codes = [502, 503, 504]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(__name__)
            
            for attempt in range(max_retries + 1):
                try:
                    response = func(*args, **kwargs)

                    # Check if the response has a status_code attribute or if we can determine status
                    if hasattr(response, 'status_code') and response.status_code in status_codes:
                        if attempt < max_retries:
                            sleep_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                            logger.warning(f"Attempt {attempt + 1} failed with status {response.status_code}, retrying in {sleep_time:.2f}s")
                            time.sleep(sleep_time)
                            continue
                    elif isinstance(response, SeedanceResponseBody) and response.error:
                        # If it's an error response, check if it's a server error that warrants retrying
                        error_details = response.error.get('status_code', None)
                        if error_details in status_codes and attempt < max_retries:
                            sleep_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                            logger.warning(f"Server error on attempt {attempt + 1}, retrying in {sleep_time:.2f}s")
                            time.sleep(sleep_time)
                            continue

                    return response
                except RequestException as e:
                    if attempt == max_retries:
                        logger.error(f"Max retries reached after {max_retries + 1} attempts: {str(e)}")
                        raise e
                    sleep_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Request failed on attempt {attempt + 1}, retrying in {sleep_time:.2f}s: {str(e)}")
                    time.sleep(sleep_time)
            return response
        return wrapper
    return decorator