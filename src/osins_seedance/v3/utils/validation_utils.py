"""Configuration validator to ensure valid parameters"""

from typing import Union


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