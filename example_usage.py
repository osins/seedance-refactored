"""Example usage of the Volces API client"""

from src.seedance.v3.models import SeedanceRequestBody, SeedanceResponseBody
from src.seedance.v3.client import seed_generations_tasks, get_seedance_models

def example_usage():
    """Example of how to use the Volces API client"""
    
    print("Getting available models...")
    models_response = get_seedance_models()
    if models_response.error:
        print(f"Error getting models: {models_response.error}")
    else:
        print(f"Available models: {models_response}")
    
    print("\nCalling the API with a sample request...")
    
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
        
        # Call the API
        response = seed_generations_tasks(request_body)
        
        if response.error:
            print(f"API Error: {response.error}")
        else:
            print(f"API Response: {response}")
            
    except ValueError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    example_usage()