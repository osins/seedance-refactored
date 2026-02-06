"""Configuration utilities for the Seedance API client."""

import os


def get_api_base_host() -> str:
    """
    Get the API base host address

    Returns:
        API base host address, without version path
    """
    return os.getenv("VOLCES_BASE_HOST") or "https://api.volces.com"