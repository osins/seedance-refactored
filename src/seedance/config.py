"""Configuration utilities for the Seedance API client."""

import os


def get_api_base_host() -> str:
    """
    获取API基础主机地址

    Returns:
        API基础主机地址，不包含版本路径
    """
    return os.getenv("VOLCES_BASE_HOST") or "https://api.volces.com"