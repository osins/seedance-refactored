"""Configuration utilities for v3 API."""

from ...config import get_api_base_host


def get_v3_api_base_url() -> str:
    """
    获取v3版本API的统一基础URL

    Returns:
        v3版本API的基础URL，格式为 {base_host}/v3
    """
    base_host = get_api_base_host()
    return f"{base_host}/v3"