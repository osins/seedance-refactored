"""Base API client for Volces API v3"""

import os
import time
import requests
from typing import Optional
from ..utils.common_utils import get_api_key
from ..model.request_body import SeedanceRequestBody
from ..model.response_body import SeedanceResponseBody
from ..config.config import get_v3_api_base_url


class BaseClient:
    """Basic API client with core functionality"""

    def __init__(self, api_key: str = None, base_url: str = None, timeout: int = 30):
        """
        Initialize the base API client.

        Args:
            api_key: API key for authentication; defaults to VOLCES_API_KEY env var
            base_url: Base URL for the API; defaults to v3 API URL
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or get_api_key()
        # If base_url is explicitly provided as parameter, use it as-is
        if base_url:
            self.base_url = base_url
        else:
            # Use centralized function to get v3 API base URL
            self.base_url = get_v3_api_base_url()
        self.timeout = timeout

    def _get_auth_headers(self) -> dict:
        """Helper method to get authentication headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def make_request(self, endpoint: str, method: str = "POST", data: dict = None) -> requests.Response:
        """
        Make a request to the API.

        Args:
            endpoint: API endpoint to call
            method: HTTP method to use
            data: Data to send with the request

        Returns:
            Response from the API
        """
        headers = self._get_auth_headers()
        
        url = f"{self.base_url}{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=self.timeout)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=self.timeout)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=self.timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return response