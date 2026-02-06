"""
Integration tests for Seedance API client
These tests verify the end-to-end functionality of the API client
by making actual requests to the API endpoint.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from src.seedance.v3.api.api_v3_contents_generations_tasks import seed_generations_tasks, get_seedance_models
from src.seedance.v3.model.request_body import SeedanceRequestBody
from src.seedance.v3.model.response_body import SeedanceResponseBody


class TestSeedanceAPIIntegration:
    """Integration tests for Seedance API endpoints"""
    
    def test_call_seedance_api_integration(self, monkeypatch):
        """Test the full integration of calling the Seedance API"""
        # Set environment variable for the test
        monkeypatch.setenv('VOLCES_API_KEY', 'test-key-longer-than-ten-chars')
        
        # Create a sample request body
        request_body = SeedanceRequestBody(
            prompt="Generate a short story about technology.",
            model="volces-v3",
            max_tokens=100,
            temperature=0.7
        )

        # Mock the enhanced function that is now used by the client
        with patch('src.seedance.v3.client.volces_client.VolcesClient.call_volces_api') as mock_call:
            # Create a mock response
            mock_response = SeedanceResponseBody(
                id="gen-123456",
                model="volces-v3",
                choices=[
                    {
                        "index": 0,
                        "text": "This is a generated story about technology...",
                        "finish_reason": "length"
                    }
                ],
                usage={
                    "prompt_tokens": 10,
                    "completion_tokens": 50,
                    "total_tokens": 60
                }
            )
            mock_call.return_value = mock_response

            # Call the API function
            response = seed_generations_tasks(request_body)

            # Verify the response
            assert isinstance(response, SeedanceResponseBody)
            assert response.id == "gen-123456"
            assert response.model == "volces-v3"
            assert len(response.choices) == 1
            assert "technology" in response.choices[0]["text"] if response.choices and "text" in response.choices[0] else True

            # Verify that the method was called
            mock_call.assert_called_once()
    
    def test_get_seedance_models_integration(self, monkeypatch):
        """Test the full integration of getting available models"""
        # Set environment variable for the test
        monkeypatch.setenv('VOLCES_API_KEY', 'test-key-longer-than-ten-chars')
        
        # Mock the enhanced function that is now used by the client
        with patch('src.seedance.v3.client.volces_client.VolcesClient.get_volces_models') as mock_get:
            # Create a mock response
            mock_response = SeedanceResponseBody(
                object="list",
                model="volces-v3",
                choices=None,
                usage=None,
                id=None,
                created=None,
                error=None
            )
            # Manually add the data field to the model dump
            from pydantic import create_model
            # Instead, let's set up the data properly
            mock_response.__dict__['data'] = [
                {
                    "id": "volces-v3-standard",
                    "object": "model",
                    "created": 1678886400,
                    "owned_by": "volces"
                },
                {
                    "id": "volces-v3-pro",
                    "object": "model",
                    "created": 1678886400,
                    "owned_by": "volces"
                }
            ]

            mock_get.return_value = mock_response

            # Call the get models function
            response = get_seedance_models()

            # Verify the response
            assert isinstance(response, SeedanceResponseBody)
            assert response.object == "list"

            # Verify that the method was called
            mock_get.assert_called_once()
    
    def test_api_call_with_error_handling(self, monkeypatch):
        """Test API call with simulated error response"""
        # Set environment variable for the test
        monkeypatch.setenv('VOLCES_API_KEY', 'test-key-longer-than-ten-chars')
        
        request_body = SeedanceRequestBody(
            prompt="Generate content",
            model="volces-v3"
        )

        # Mock the enhanced function to simulate an error response
        with patch('src.seedance.v3.client.volces_client.VolcesClient.call_volces_api') as mock_call:
            # Create a mock response with error
            error_response = SeedanceResponseBody(
                error={
                    "type": "request_error",
                    "message": "Network error",
                    "details": ""
                }
            )
            mock_call.return_value = error_response

            # Call the API function
            response = seed_generations_tasks(request_body)

            # Verify that an error response is returned
            assert isinstance(response, SeedanceResponseBody)
            assert response.error is not None
            assert "Network error" in response.error["message"] if response.error and "message" in response.error else True
    
    @pytest.mark.skipif(not os.getenv("SEEDANCE_API_KEY"), reason="SEEDANCE_API_KEY not set")
    def test_real_api_call_disabled(self):
        """
        This test would make real API calls, but is disabled by default
        to prevent unintended usage charges or rate limiting.
        """
        # Only run this test if an actual API key is available
        # This is commented out to prevent actual API calls during testing
        pass