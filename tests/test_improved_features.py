"""Tests for the improved features of the Volces API client"""

import os
import pytest
from unittest.mock import patch, MagicMock
from src.seedance.v3 import VolcesClient, SeedanceRequestBody, SeedanceResponseBody
from src.seedance.v3.utils.enums import APIErrorType
from src.seedance.v3.utils.validation_utils import ConfigValidator


class TestImprovedFeatures:
    """Tests for improved features"""
    
    def test_config_validator_api_key(self):
        """Test the configuration validator for API key"""
        # Valid API key should pass
        assert ConfigValidator.validate_api_key("valid_api_key_123") == True
        
        # Empty API key should raise error
        with pytest.raises(ValueError, match="API key is required"):
            ConfigValidator.validate_api_key("")
        
        # Short API key should raise error
        with pytest.raises(ValueError, match="Invalid API key format"):
            ConfigValidator.validate_api_key("short")
    
    def test_config_validator_base_url(self):
        """Test the configuration validator for base URL"""
        # Valid URL should pass
        assert ConfigValidator.validate_base_url("https://api.example.com") == True
        assert ConfigValidator.validate_base_url("http://localhost:8080") == True
        
        # Invalid URL should raise error
        with pytest.raises(ValueError, match="must start with http:// or https://"):
            ConfigValidator.validate_base_url("ftp://api.example.com")
        
        with pytest.raises(ValueError, match="must start with http:// or https://"):
            ConfigValidator.validate_base_url("invalid-url")
    
    def test_volces_client_initialization_with_validation(self):
        """Test that VolcesClient validates configuration on initialization"""
        # Should succeed with valid configuration
        os.environ['VOLCES_API_KEY'] = 'valid-test-key-12345'
        
        client = VolcesClient(base_url="https://api.volces.com/v3")
        assert client.api_key == 'valid-test-key-12345'
        assert client.base_url == "https://api.volces.com/v3"
        
        # Clean up
        del os.environ['VOLCES_API_KEY']
    
    def test_volces_client_fails_with_invalid_config(self):
        """Test that VolcesClient fails with invalid configuration"""
        # Should fail with invalid API key
        os.environ['VOLCES_API_KEY'] = 'short'
        
        with pytest.raises(ValueError, match="Invalid API key format"):
            VolcesClient()
        
        # Clean up
        del os.environ['VOLCES_API_KEY']
    
    def test_cache_key_generation(self):
        """Test cache key generation for deterministic requests"""
        from src.seedance.v3.client.cache_mechanism import CacheMechanism
        
        cache_mechanism = CacheMechanism()

        # Deterministic request (temperature = 0) should generate cache key
        deterministic_request = SeedanceRequestBody(
            prompt="Test prompt",
            model="volces-v3",
            temperature=0.0  # Deterministic
        )

        cache_key = cache_mechanism.generate_cache_key(deterministic_request)
        assert cache_key is not None
        assert isinstance(cache_key, str)
        assert len(cache_key) == 32  # MD5 hash length

        # Non-deterministic request (temperature != 0) should not generate cache key
        non_deterministic_request = SeedanceRequestBody(
            prompt="Test prompt",
            model="volces-v3",
            temperature=0.7  # Non-deterministic
        )

        cache_key = cache_mechanism.generate_cache_key(non_deterministic_request)
        assert cache_key is None
    
    def test_cache_functionality(self):
        """Test caching functionality"""
        from src.seedance.v3.client.cache_mechanism import CacheMechanism

        cache_mechanism = CacheMechanism()

        # Create a deterministic request
        request = SeedanceRequestBody(
            prompt="Cache test prompt",
            model="volces-v3",
            temperature=0.0,
            max_tokens=10
        )

        # Test cache key generation
        cache_key = cache_mechanism.generate_cache_key(request)
        assert cache_key is not None

        # Test setting and getting cached response
        test_response = SeedanceResponseBody(id="cached", model="test")
        cache_mechanism.set_cache_response(cache_key, test_response)

        cached_response = cache_mechanism.get_cached_response(cache_key)
        assert cached_response is not None
        assert cached_response.id == "cached"
        assert cached_response.model == "test"
    
    def test_logging_in_client_operations(self, monkeypatch, caplog):
        """Test that logging works in client operations"""
        os.environ['VOLCES_API_KEY'] = 'valid-test-key-12345'
        
        client = VolcesClient()
        
        # Create a request
        request = SeedanceRequestBody(
            prompt="Test prompt for logging",
            model="volces-v3"
        )
        
        # Mock the API call to avoid actual network request
        def mock_post(*args, **kwargs):
            import requests
            response = MagicMock()
            response.status_code = 404  # Simulate not found
            response.text = "Not Found"
            response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Error")
            return response
        
        import logging
        with caplog.at_level(logging.INFO):
            monkeypatch.setattr(client.session, 'post', mock_post)
            
            response = client.call_volces_api(request)
            
            # Check that logging occurred
            assert any("Making API call with prompt:" in record.message 
                      for record in caplog.records)
            # The API call will fail due to the mock, so we expect a failure message
            assert any("API call failed" in record.message 
                      for record in caplog.records)
        
        # Clean up
        del os.environ['VOLCES_API_KEY']


def test_error_handling_improvements():
    """Test improved error handling"""
    # Verify that error types are defined correctly
    assert hasattr(APIErrorType, 'AUTHENTICATION_ERROR')
    assert hasattr(APIErrorType, 'VALIDATION_ERROR')
    assert hasattr(APIErrorType, 'RATE_LIMIT_ERROR')
    assert hasattr(APIErrorType, 'SERVER_ERROR')
    assert hasattr(APIErrorType, 'NETWORK_ERROR')
    
    # Verify values
    assert APIErrorType.AUTHENTICATION_ERROR.value == "authentication_error"
    assert APIErrorType.VALIDATION_ERROR.value == "validation_error"
    assert APIErrorType.RATE_LIMIT_ERROR.value == "rate_limit_error"
    assert APIErrorType.SERVER_ERROR.value == "server_error"
    assert APIErrorType.NETWORK_ERROR.value == "network_error"