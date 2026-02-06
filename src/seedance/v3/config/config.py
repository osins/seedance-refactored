"""Configuration utilities for v3 API."""

from ...config import get_api_base_host


def get_v3_api_base_url() -> str:
    """
    Get the unified base URL for v3 API

    Returns:
        Base URL for v3 API, in the format {base_host}/v3
    """
    base_host = get_api_base_host()
    return f"{base_host}/v3"