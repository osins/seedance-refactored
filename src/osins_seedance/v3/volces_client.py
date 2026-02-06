"""Advanced API Client for Volces API v3 with improved error handling and retry logic"""

import os
import time
import random
import requests
import hashlib
from enum import Enum
from typing import Optional
from functools import wraps, lru_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .models import SeedanceRequestBody, SeedanceResponseBody
from .utils import get_v3_api_base_url
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIErrorType(Enum):
    """Enumeration of different API error types"""
    AUTHENTICATION_ERROR = "authentication_error"
    VALIDATION_ERROR = "validation_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    SERVER_ERROR = "server_error"
    NETWORK_ERROR = "network_error"


class ConfigValidator:
    """Configuration validator to ensure valid parameters"""

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format and presence"""
        if not api_key:
            raise ValueError("API key is required")
        if not isinstance(api_key, str) or len(api_key) < 10:  # Realistic minimum length
            raise ValueError("Invalid API key format - must be at least 10 characters")
        return True

    @staticmethod
    def validate_base_url(base_url: str) -> bool:
        """Validate base URL format"""
        if not base_url.startswith(('http://', 'https://')):
            raise ValueError("Base URL must start with http:// or https://")
        return True


def retry_on_failure(max_retries=3, backoff_factor=1.0, status_codes=[502, 503, 504]):
    """
    Decorator to implement retry logic with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Factor for exponential backoff
        status_codes: HTTP status codes that should trigger a retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
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
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries:
                        logger.error(f"Max retries reached after {max_retries + 1} attempts: {str(e)}")
                        raise e
                    sleep_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Request failed on attempt {attempt + 1}, retrying in {sleep_time:.2f}s: {str(e)}")
                    time.sleep(sleep_time)
            return response
        return wrapper
    return decorator


class VolcesClient:
    """Enhanced API client with connection pooling, retry logic, and better error handling"""

    def __init__(self, api_key: str = None, base_url: str = None, timeout: int = 30):
        """
        Initialize the Volces API client.

        Args:
            api_key: API key for authentication; defaults to VOLCES_API_KEY env var
            base_url: Base URL for the API; defaults to environment or default URL
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("VOLCES_API_KEY")
        # If base_url is explicitly provided as parameter, use it as-is
        if base_url:
            self.base_url = base_url
        else:
            # Use centralized function to get v3 API base URL
            self.base_url = get_v3_api_base_url()  # Version path is fixed for v3 API
        self.timeout = timeout

        # Validate configuration
        ConfigValidator.validate_api_key(self.api_key)
        ConfigValidator.validate_base_url(self.base_url)

        # Configure session with retry strategy and connection pooling
        self.session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],  # Status codes to retry
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]  # Methods to retry
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json"
        })

        # Initialize cache
        self._cache = {}

    def _generate_cache_key(self, request_body: SeedanceRequestBody) -> str:
        """Generate a cache key based on request parameters"""
        # Only cache deterministic requests (temperature = 0)
        if request_body.temperature != 0:
            return None

        cacheable_params = ('prompt', 'model', 'max_tokens', 'temperature')
        cache_data = {k: v for k, v in request_body.model_dump().items() if k in cacheable_params and v is not None}
        cache_str = str(sorted(cache_data.items()))
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[SeedanceResponseBody]:
        """Get response from cache if available"""
        if cache_key and cache_key in self._cache:
            cached_at, response = self._cache[cache_key]
            # Check if cache is still valid (for simplicity, we'll assume it's always valid for this example)
            return response
        return None

    def _set_cache_response(self, cache_key: str, response: SeedanceResponseBody):
        """Store response in cache"""
        if cache_key:
            self._cache[cache_key] = (time.time(), response)

    def _get_auth_headers(self) -> dict:
        """Helper method to get authentication headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _handle_request_exception(self, e: requests.exceptions.RequestException, operation: str = "") -> SeedanceResponseBody:
        """Helper method to handle request exceptions."""
        logger.error(f"Request error during {operation}: {str(e)}")

        error_details = ""
        status_code = None
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.text
                status_code = e.response.status_code
            except Exception:
                error_details = str(getattr(e.response, 'text', ''))

        # Determine error type based on the exception
        error_type = APIErrorType.NETWORK_ERROR
        if status_code == 401 or "authentication" in str(e).lower():
            error_type = APIErrorType.AUTHENTICATION_ERROR
        elif status_code in [500, 502, 503, 504]:
            error_type = APIErrorType.SERVER_ERROR
        elif status_code == 429:
            error_type = APIErrorType.RATE_LIMIT_ERROR

        return SeedanceResponseBody(
            error={
                "type": error_type.value,
                "message": str(e),
                "details": error_details,
                "status_code": status_code
            }
        )

    def _handle_general_exception(self, e: Exception, operation: str = "") -> SeedanceResponseBody:
        """Helper method to handle general exceptions."""
        logger.error(f"General error during {operation}: {str(e)}")

        return SeedanceResponseBody(
            error={
                "type": APIErrorType.VALIDATION_ERROR.value if isinstance(e, ValueError) else "unknown_error",
                "message": str(e)
            }
        )

    @retry_on_failure(max_retries=3, backoff_factor=1.0, status_codes=[502, 503, 504])
    def call_volces_api(self, request_body: SeedanceRequestBody) -> SeedanceResponseBody:
        """
        Call the Volces API with the given request body.

        Args:
            request_body: Request body containing parameters for the API call

        Returns:
            Response body from the API
        """
        # Log the API call
        logger.info(f"Making API call with prompt: {request_body.prompt[:50]}{'...' if len(request_body.prompt) > 50 else ''}")

        start_time = time.time()

        try:
            # Validate input
            if not isinstance(request_body, SeedanceRequestBody):
                raise TypeError("request_body must be an instance of SeedanceRequestBody")

            # Check cache for deterministic requests
            cache_key = self._generate_cache_key(request_body)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                logger.info("Returning cached response")
                duration = time.time() - start_time
                logger.info(f"API call completed via cache in {duration:.2f}s")
                return cached_response

            headers = self._get_auth_headers()

            response = self.session.post(
                f"{self.base_url}/generate",
                headers=headers,
                json=request_body.model_dump(),
                timeout=self.timeout
            )

            duration = time.time() - start_time
            logger.info(f"API call completed in {duration:.2f}s with status {response.status_code}")

            # Check for HTTP errors
            response.raise_for_status()

            # Parse response JSON
            response_json = response.json()

            # Create response model
            result = SeedanceResponseBody(**response_json)

            # Cache deterministic responses
            if cache_key:
                self._set_cache_response(cache_key, result)

            return result

        except requests.exceptions.HTTPError as e:
            duration = time.time() - start_time
            logger.error(f"API call failed after {duration:.2f}s with HTTP error: {str(e)}")
            return self._handle_request_exception(e, "call_volces_api")
        except requests.exceptions.ConnectionError as e:
            duration = time.time() - start_time
            logger.error(f"API call failed after {duration:.2f}s with connection error: {str(e)}")
            return self._handle_request_exception(e, "call_volces_api")
        except requests.exceptions.Timeout as e:
            duration = time.time() - start_time
            logger.error(f"API call failed after {duration:.2f}s with timeout: {str(e)}")
            return self._handle_request_exception(e, "call_volces_api")
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            logger.error(f"API call failed after {duration:.2f}s with request error: {str(e)}")
            return self._handle_request_exception(e, "call_volces_api")
        except ValueError as e:  # JSON decode error
            duration = time.time() - start_time
            logger.error(f"API call failed after {duration:.2f}s with JSON decode error: {str(e)}")
            return self._handle_general_exception(e, "call_volces_api")
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"API call failed after {duration:.2f}s with unexpected error: {str(e)}")
            return self._handle_general_exception(e, "call_volces_api")

    @retry_on_failure(max_retries=3, backoff_factor=1.0, status_codes=[502, 503, 504])
    def get_volces_models(self) -> SeedanceResponseBody:
        """
        Get available models from Volces API.

        Returns:
            Response body containing available models
        """
        logger.info(f"Fetching models from {self.base_url}/models")

        start_time = time.time()

        try:
            headers = self._get_auth_headers()

            response = self.session.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=self.timeout
            )

            duration = time.time() - start_time
            logger.info(f"Models fetch completed in {duration:.2f}s with status {response.status_code}")

            # Check for HTTP errors
            response.raise_for_status()

            # Parse response JSON
            response_json = response.json()

            # Return as response model
            return SeedanceResponseBody(**response_json)

        except requests.exceptions.HTTPError as e:
            duration = time.time() - start_time
            logger.error(f"Models fetch failed after {duration:.2f}s with HTTP error: {str(e)}")
            return self._handle_request_exception(e, "get_volces_models")
        except requests.exceptions.ConnectionError as e:
            duration = time.time() - start_time
            logger.error(f"Models fetch failed after {duration:.2f}s with connection error: {str(e)}")
            return self._handle_request_exception(e, "get_volces_models")
        except requests.exceptions.Timeout as e:
            duration = time.time() - start_time
            logger.error(f"Models fetch failed after {duration:.2f}s with timeout: {str(e)}")
            return self._handle_request_exception(e, "get_volces_models")
        except requests.exceptions.RequestException as e:
            duration = time.time() - start_time
            logger.error(f"Models fetch failed after {duration:.2f}s with request error: {str(e)}")
            return self._handle_request_exception(e, "get_volces_models")
        except ValueError as e:  # JSON decode error
            duration = time.time() - start_time
            logger.error(f"Models fetch failed after {duration:.2f}s with JSON decode error: {str(e)}")
            return self._handle_general_exception(e, "get_volces_models")
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Models fetch failed after {duration:.2f}s with unexpected error: {str(e)}")
            return self._handle_general_exception(e, "get_volces_models")