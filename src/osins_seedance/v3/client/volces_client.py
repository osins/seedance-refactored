"""Main API Client for Volces API v3 with all enhanced features"""

import os
import time
import hashlib
from typing import Optional
from requests.sessions import Session
from requests.exceptions import ConnectionError, Timeout
from ..model.request_body import SeedanceRequestBody
from ..model.response_body import SeedanceResponseBody
from ..config.config import get_v3_api_base_url
from ..utils.validation_utils import ConfigValidator
from ..utils.cache_utils import generate_cache_key, get_cached_response, set_cache_response
from ..utils.error_utils import handle_request_exception, handle_general_exception
from ..utils.retry_utils import retry_on_failure
from .base_client import BaseClient
from .connection_pool import ConnectionPoolManager
from .cache_mechanism import CacheMechanism
from .error_handling import ErrorHandling
from .session_management import SessionManagement
from .performance_optimization import PerformanceOptimization
import logging


class VolcesClient:
    """Enhanced API client with all features: connection pooling, retry logic, caching, and better error handling"""

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

        # Initialize components
        self.connection_pool_manager = ConnectionPoolManager()
        self.cache_mechanism = CacheMechanism()
        self.error_handling = ErrorHandling()
        self.session_management = SessionManagement()
        self.performance_optimization = PerformanceOptimization()

        # Configure session with retry strategy and connection pooling
        self.session = self.session_management.create_session({
            "Content-Type": "application/json"
        })

        # Initialize cache
        self._cache = {}

    def _get_auth_headers(self) -> dict:
        """Helper method to get authentication headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    @retry_on_failure(max_retries=3, backoff_factor=1.0, status_codes=[502, 503, 504])
    def call_volces_api(self, request_body: SeedanceRequestBody) -> SeedanceResponseBody:
        """
        Call the Volces API with the given request body.

        Args:
            request_body: Request body containing parameters for the API call

        Returns:
            Response body from the API
        """
        logger = logging.getLogger(__name__)

        # Log the API call
        logger.info(f"Making API call with prompt: {request_body.prompt[:50]}{'...' if len(request_body.prompt) > 50 else ''}")

        start_time = time.time()

        try:
            # Validate input
            if not isinstance(request_body, SeedanceRequestBody):
                error_response = SeedanceResponseBody(
                    error={
                        "type": "validation_error",
                        "message": "request_body must be an instance of SeedanceRequestBody"
                    }
                )
                return error_response

            # Check cache for deterministic requests
            cache_key = self.cache_mechanism.generate_cache_key(request_body)
            cached_response = self.cache_mechanism.get_cached_response(cache_key)
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
                self.cache_mechanism.set_cache_response(cache_key, result)

            return result

        except Exception as e:
            duration = time.time() - start_time
            if isinstance(e, (ConnectionError, Timeout)):
                logger.error(f"API call failed after {duration:.2f}s with connection/timeout error: {str(e)}")
                return self.error_handling.handle_request_exception(e, "call_volces_api")
            else:
                logger.error(f"API call failed after {duration:.2f}s with unexpected error: {str(e)}")
                return self.error_handling.handle_general_exception(e, "call_volces_api")

    @retry_on_failure(max_retries=3, backoff_factor=1.0, status_codes=[502, 503, 504])
    def get_volces_models(self) -> SeedanceResponseBody:
        """
        Get available models from Volces API.

        Returns:
            Response body containing available models
        """
        logger = logging.getLogger(__name__)
        
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

        except Exception as e:
            duration = time.time() - start_time
            if isinstance(e, (ConnectionError, Timeout)):
                logger.error(f"Models fetch failed after {duration:.2f}s with connection/timeout error: {str(e)}")
                return self.error_handling.handle_request_exception(e, "get_volces_models")
            else:
                logger.error(f"Models fetch failed after {duration:.2f}s with unexpected error: {str(e)}")
                return self.error_handling.handle_general_exception(e, "get_volces_models")

    def close(self):
        """Close the client session and clean up resources."""
        self.session.close()