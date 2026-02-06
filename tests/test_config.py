"""Tests for configuration utilities."""

import os
import pytest
from src.seedance.config import get_api_base_host
from src.seedance.v3.config.config import get_v3_api_base_url


class TestConfigFunctions:
    """Test configuration utility functions."""

    def test_get_api_base_host_default(self):
        """Test getting default API base host when no environment variable is set."""
        # Ensure VOLCES_BASE_HOST is not set
        if 'VOLCES_BASE_HOST' in os.environ:
            del os.environ['VOLCES_BASE_HOST']
            
        base_host = get_api_base_host()
        assert base_host == "https://api.volces.com"

    def test_get_api_base_host_custom(self):
        """Test getting custom API base host from environment variable."""
        # Set custom base host
        os.environ['VOLCES_BASE_HOST'] = 'https://custom-api.com'
        
        base_host = get_api_base_host()
        assert base_host == 'https://custom-api.com'
        
        # Clean up
        del os.environ['VOLCES_BASE_HOST']

    def test_get_v3_api_base_url_default(self):
        """Test getting default v3 API base URL."""
        # Ensure VOLCES_BASE_HOST is not set
        if 'VOLCES_BASE_HOST' in os.environ:
            del os.environ['VOLCES_BASE_HOST']
            
        base_url = get_v3_api_base_url()
        assert base_url == "https://api.volces.com/v3"

    def test_get_v3_api_base_url_custom(self):
        """Test getting custom v3 API base URL from environment variable."""
        # Set custom base host
        os.environ['VOLCES_BASE_HOST'] = 'https://custom-api.com'
        
        base_url = get_v3_api_base_url()
        assert base_url == 'https://custom-api.com/v3'
        
        # Clean up
        del os.environ['VOLCES_BASE_HOST']

    def test_v3_url_calls_base_host_function(self):
        """Test that v3 URL function properly calls the base host function."""
        # Set custom base host
        os.environ['VOLCES_BASE_HOST'] = 'https://test-api.com'
        
        base_host = get_api_base_host()
        v3_url = get_v3_api_base_url()
        
        assert base_host == 'https://test-api.com'
        assert v3_url == 'https://test-api.com/v3'
        
        # Clean up
        del os.environ['VOLCES_BASE_HOST']


def test_config_functions_integration():
    """Integration test for config functions."""
    # Test with default values
    if 'VOLCES_BASE_HOST' in os.environ:
        del os.environ['VOLCES_BASE_HOST']
    
    default_host = get_api_base_host()
    default_v3_url = get_v3_api_base_url()
    
    assert default_host == "https://api.volces.com"
    assert default_v3_url == "https://api.volces.com/v3"
    
    # Test with custom values
    os.environ['VOLCES_BASE_HOST'] = 'https://integration-test.com'
    
    custom_host = get_api_base_host()
    custom_v3_url = get_v3_api_base_url()
    
    assert custom_host == "https://integration-test.com"
    assert custom_v3_url == "https://integration-test.com/v3"
    
    # Clean up
    del os.environ['VOLCES_BASE_HOST']