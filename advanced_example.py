"""Advanced example usage of the Volces API client with enhanced features"""

import os
from src.seedance.v3 import VolcesClient, SeedanceRequestBody, SeedanceResponseBody, APIErrorType

def advanced_example():
    """Example of how to use the enhanced Volces API client"""
    
    # Initialize the client (uses VOLCES_API_KEY from environment)
    try:
        client = VolcesClient()
        print("VolcesClient initialized successfully")
    except ValueError as e:
        print(f"Failed to initialize client: {e}")
        print("Please set VOLCES_API_KEY environment variable")
        return
    
    print("\n1. Getting available models...")
    models_response = client.get_volces_models()
    if models_response.error:
        print(f"Error getting models: {models_response.error}")
        if models_response.error.get('type') == APIErrorType.AUTHENTICATION_ERROR.value:
            print("Authentication error - check your API key")
    else:
        print(f"Available models: {models_response}")
    
    print("\n2. Calling the API with a sample request...")
    
    # Create a sample request body with enhanced validation
    try:
        request_body = SeedanceRequestBody(
            prompt="Generate a short story about a robot learning to paint.",
            model="volces-v3",
            max_tokens=200,
            temperature=0.7,
            top_p=0.9
        )
        
        print(f"Created request: {request_body}")
        
        # Call the API using the enhanced client
        response = client.call_volces_api(request_body)
        
        if response.error:
            print(f"API Error: {response.error}")
            # Check error type for specific handling
            if response.error.get('type') == APIErrorType.RATE_LIMIT_ERROR.value:
                print("Rate limit reached - consider implementing delays")
            elif response.error.get('type') == APIErrorType.AUTHENTICATION_ERROR.value:
                print("Authentication failed - check your API key")
        else:
            print(f"API Response received successfully: {response}")
            
    except ValueError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def basic_compatibility_example():
    """Example showing backward compatibility with original functions"""
    print("\n3. Using backward-compatible functions...")
    
    # These still work as before for compatibility
    from src.seedance.v3.client import call_seedance_api, get_seedance_models
    from src.seedance.v3.model.request_body import SeedanceRequestBody
    
    try:
        # Create a request
        request = SeedanceRequestBody(
            prompt="Hello, world!",
            model="volces-v3"
        )
        
        # Use the backward-compatible function
        response = call_seedance_api(request)
        print(f"Backward compatible call result: Error={response.error is not None}")
        
    except Exception as e:
        print(f"Compatibility example error: {e}")

if __name__ == "__main__":
    advanced_example()
    basic_compatibility_example()