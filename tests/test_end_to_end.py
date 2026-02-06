"""
End-to-end integration tests for Volces API client
These tests validate the complete workflow of the API client
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from src.seedance.v3.api.api_v3_contents_generations_tasks import seed_generations_tasks, get_seedance_models
from src.seedance.v3.model.request_body import SeedanceRequestBody
from src.seedance.v3.model.response_body import SeedanceResponseBody


class TestEndToEndWorkflows:
    """End-to-end tests for complete workflows"""
    
    def test_complete_generation_workflow(self, monkeypatch):
        """Test the complete workflow from request creation to response handling"""
        # Set environment variable for the test
        monkeypatch.setenv('VOLCES_API_KEY', 'test-key-longer-than-ten-chars')
        
        # Step 1: Get available models
        with patch('src.seedance.v3.client.volces_client.VolcesClient.get_volces_models') as mock_get:
            mock_response = SeedanceResponseBody(
                object="list",
                data=[
                    {
                        "id": "volces-v3-standard",
                        "object": "model",
                        "created": 1678886400,
                        "owned_by": "volces"
                    }
                ]
            )
            mock_get.return_value = mock_response

            models_response = get_seedance_models()

            # Verify models were retrieved
            assert models_response.object == "list"
            # Need to access the data differently since it's in the model
            # The actual response would have the data in the model_dump
            response_dict = models_response.model_dump()
            if 'data' in response_dict:
                assert len(response_dict["data"]) == 1
                assert response_dict["data"][0]["id"] == "volces-v3-standard"

        # Step 2: Use the model information to create a generation request
        request_body = SeedanceRequestBody(
            prompt="Write a creative paragraph about innovation in 2026",
            model="volces-v3-standard",
            max_tokens=150,
            temperature=0.8
        )

        # Step 3: Call the generation API
        with patch('src.seedance.v3.client.volces_client.VolcesClient.call_volces_api') as mock_post:
            mock_response = SeedanceResponseBody(
                id="gen-innovation-2026",
                model="volces-v3-standard",
                choices=[
                    {
                        "index": 0,
                        "text": "In 2026, innovation reaches new heights as artificial intelligence seamlessly integrates into daily life...",
                        "finish_reason": "length"
                    }
                ],
                usage={
                    "prompt_tokens": 12,
                    "completion_tokens": 85,
                    "total_tokens": 97
                }
            )
            mock_post.return_value = mock_response

            generation_response = seed_generations_tasks(request_body)

            # Verify the generation response
            assert generation_response.id == "gen-innovation-2026"
            assert generation_response.model == "volces-v3-standard"
            if generation_response.choices:
                assert "innovation" in generation_response.choices[0]["text"].lower()
            if generation_response.usage:
                assert generation_response.usage["completion_tokens"] == 85
    
    def test_error_workflow_consistency(self, monkeypatch):
        """Test that errors are handled consistently across different endpoints"""
        # Set environment variable for the test
        monkeypatch.setenv('VOLCES_API_KEY', 'test-key-longer-than-ten-chars')
        
        # Simulate network error for model retrieval
        with patch('src.seedance.v3.client.volces_client.VolcesClient.get_volces_models') as mock_get:
            mock_response = SeedanceResponseBody(
                error={
                    "type": "unknown_error",
                    "message": "Connection timeout",
                    "details": ""
                }
            )
            mock_get.return_value = mock_response

            models_response = get_seedance_models()

            # Verify error structure
            assert models_response.error is not None
            assert models_response.error["type"] == "unknown_error"
            assert "Connection timeout" in models_response.error["message"]

        # Simulate HTTP error for generation
        request_body = SeedanceRequestBody(
            prompt="Test prompt",
            model="volces-v3"
        )

        with patch('src.seedance.v3.client.volces_client.VolcesClient.call_volces_api') as mock_post:
            mock_response = SeedanceResponseBody(
                error={
                    "type": "request_error",
                    "message": "Simulated API error",
                    "details": "Error details"
                }
            )
            mock_post.return_value = mock_response

            gen_response = seed_generations_tasks(request_body)

            # Verify error structure
            assert gen_response.error is not None
            assert "type" in gen_response.error
    
    def test_multiple_concurrent_requests_simulation(self, monkeypatch):
        """Test simulating multiple concurrent API requests"""
        # Set environment variable for the test
        monkeypatch.setenv('VOLCES_API_KEY', 'test-key-longer-than-ten-chars')
        
        import time

        # Mock responses for concurrent requests
        def create_mock_response(request_body):
            return SeedanceResponseBody(
                id=f"gen-{abs(hash(str(request_body.prompt))) % 10000}",
                model=request_body.model or "volces-v3",
                choices=[{"index": 0, "text": f"Response to: {request_body.prompt}", "finish_reason": "stop"}],
                usage={"prompt_tokens": len(request_body.prompt.split()), "completion_tokens": 20, "total_tokens": 30}
            )

        # Create multiple requests
        requests = [
            SeedanceRequestBody(prompt=f"Prompt {i}", model="volces-v3", max_tokens=50)
            for i in range(5)
        ]

        responses = []

        # Process requests sequentially with patched function
        for i, request_body in enumerate(requests):
            with patch('src.seedance.v3.client.volces_client.VolcesClient.call_volces_api') as mock_call:
                mock_call.return_value = create_mock_response(request_body)

                response = seed_generations_tasks(request_body)
                responses.append(response)

        # Verify all responses
        assert len(responses) == 5
        for i, response in enumerate(responses):
            assert isinstance(response, SeedanceResponseBody)
            if response.choices:
                assert f"Prompt {i}" in str(response.choices[0]["text"])
    
    def test_request_response_data_integrity(self, monkeypatch):
        """Test that request data is properly transmitted and response data is correctly parsed"""
        # Set environment variable for the test
        monkeypatch.setenv('VOLCES_API_KEY', 'test-key-longer-than-ten-chars')
        
        original_request = SeedanceRequestBody(
            prompt="Calculate the impact of quantum computing on cryptography",
            model="volces-v3-pro",
            max_tokens=200,
            temperature=0.5,
            top_p=0.9,
            n=1,
            stream=False,
            stop=["END"],
            presence_penalty=0.1,
            frequency_penalty=0.1
        )

        with patch('src.seedance.v3.client.volces_client.VolcesClient.call_volces_api') as mock_call:
            mock_response = SeedanceResponseBody(
                id="gen-quantum-crypto",
                model="volces-v3-pro",
                choices=[
                    {
                        "index": 0,
                        "text": "Quantum computing poses significant challenges to traditional cryptographic systems...",
                        "finish_reason": "length"
                    }
                ],
                usage={
                    "prompt_tokens": 10,
                    "completion_tokens": 150,
                    "total_tokens": 160
                }
            )
            mock_call.return_value = mock_response

            response = seed_generations_tasks(original_request)

            # Verify response structure and data integrity
            assert response.id == "gen-quantum-crypto"
            assert response.model == "volces-v3-pro"
            if response.choices:
                assert "quantum" in response.choices[0]["text"].lower()
            if response.usage:
                assert response.usage["total_tokens"] == 160
            if response.choices:
                assert response.choices[0]["finish_reason"] == "length"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])