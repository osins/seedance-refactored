"""Tests for the Seedance API client."""

import pytest
from src.seedance.v3.client import call_seedance_api, get_seedance_models
from src.seedance.v3.models import SeedanceRequestBody, SeedanceResponseBody


def test_seedance_request_body_creation():
    """Test creating a SeedanceRequestBody instance."""
    request_body = SeedanceRequestBody(
        prompt="Test prompt",
        max_tokens=50
    )
    assert request_body.prompt == "Test prompt"
    assert request_body.max_tokens == 50


def test_seedance_response_body_creation():
    """Test creating a SeedanceResponseBody instance."""
    response_body = SeedanceResponseBody(
        id="test-id",
        model="test-model"
    )
    assert response_body.id == "test-id"
    assert response_body.model == "test-model"


def test_call_seedance_api_with_valid_request(monkeypatch):
    """Test calling the Seedance API with a valid request."""
    # Temporarily set the API key for the test
    import os
    original_key = os.environ.get('VOLCES_API_KEY')
    os.environ['VOLCES_API_KEY'] = 'test-key-for-testing'
    
    try:
        # Mock the requests.post to prevent actual API calls
        def mock_post(*args, **kwargs):
            import requests
            response = requests.Response()
            response.status_code = 404  # Simulate API endpoint not found
            import json
            response._content = json.dumps({"error": "Not Found"}).encode('utf-8')
            return response

        monkeypatch.setattr("src.seedance.v3.client.requests.post", mock_post)
        
        request_body = SeedanceRequestBody(
            prompt="Test prompt for API call"
        )
        
        # Since we're mocking the response, this should handle the error gracefully
        response = call_seedance_api(request_body)
        assert isinstance(response, SeedanceResponseBody)
    finally:
        # Restore original key if it existed, or remove if we added it
        if original_key is not None:
            os.environ['VOLCES_API_KEY'] = original_key
        elif 'VOLCES_API_KEY' in os.environ:
            del os.environ['VOLCES_API_KEY']


def test_get_seedance_models(monkeypatch):
    """Test getting available models from the API."""
    # Temporarily set the API key for the test
    import os
    original_key = os.environ.get('VOLCES_API_KEY')
    os.environ['VOLCES_API_KEY'] = 'test-key-for-testing'
    
    try:
        # Mock the requests.get to prevent actual API calls
        def mock_get(*args, **kwargs):
            import requests
            response = requests.Response()
            response.status_code = 404  # Simulate API endpoint not found
            import json
            response._content = json.dumps({"error": "Not Found"}).encode('utf-8')
            return response

        monkeypatch.setattr("src.seedance.v3.client.requests.get", mock_get)
        
        # This should handle the error gracefully
        response = get_seedance_models()
        assert isinstance(response, SeedanceResponseBody)
    finally:
        # Restore original key if it existed, or remove if we added it
        if original_key is not None:
            os.environ['VOLCES_API_KEY'] = original_key
        elif 'VOLCES_API_KEY' in os.environ:
            del os.environ['VOLCES_API_KEY']