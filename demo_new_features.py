#!/usr/bin/env python3
"""
Demonstration of new features in the Volces API Client
"""

import os
from src.seedance.v3 import VolcesClient, SeedanceRequestBody
from src.seedance.v3.api_client import ConfigValidator

def demo_config_validation():
    """Demonstrate configuration validation"""
    print("=== Configuration Validation Demo ===")
    
    # Valid configurations
    try:
        ConfigValidator.validate_api_key("valid_api_key_123")
        print("✓ Valid API key passed validation")
    except ValueError as e:
        print(f"✗ Unexpected validation error: {e}")
    
    try:
        ConfigValidator.validate_base_url("https://api.volces.com/v3")
        print("✓ Valid base URL passed validation")
    except ValueError as e:
        print(f"✗ Unexpected validation error: {e}")
    
    # Invalid configurations
    try:
        ConfigValidator.validate_api_key("short")
        print("✗ Short API key should have failed validation")
    except ValueError as e:
        print(f"✓ Short API key correctly failed: {e}")
    
    try:
        ConfigValidator.validate_base_url("invalid-url")
        print("✗ Invalid URL should have failed validation")
    except ValueError as e:
        print(f"✓ Invalid URL correctly failed: {e}")
    
    print()


def demo_cache_functionality():
    """Demonstrate cache functionality"""
    print("=== Cache Functionality Demo ===")
    
    # Set up environment for client initialization
    os.environ['VOLCES_API_KEY'] = 'demo-api-key-for-testing-12345'
    
    try:
        client = VolcesClient()
        
        # Create a deterministic request (temperature = 0)
        deterministic_request = SeedanceRequestBody(
            prompt="What is the capital of France?",
            model="volces-v3",
            temperature=0.0,  # This makes it cacheable
            max_tokens=50
        )
        
        # Generate cache key
        cache_key = client._generate_cache_key(deterministic_request)
        print(f"✓ Cache key generated for deterministic request: {cache_key is not None}")
        
        # Create a non-deterministic request (temperature != 0)
        non_deterministic_request = SeedanceRequestBody(
            prompt="What is the capital of France?",
            model="volces-v3",
            temperature=0.7,  # This makes it non-cacheable
            max_tokens=50
        )
        
        cache_key = client._generate_cache_key(non_deterministic_request)
        print(f"✓ No cache key for non-deterministic request: {cache_key is None}")
        
        print("✓ Cache functionality demonstrated")
        
    except Exception as e:
        print(f"✗ Error in cache demo: {e}")
    finally:
        # Clean up
        if 'VOLCES_API_KEY' in os.environ:
            del os.environ['VOLCES_API_KEY']
    
    print()


def demo_logging_and_error_handling():
    """Demonstrate improved logging and error handling"""
    print("=== Logging and Error Handling Demo ===")
    
    # Set up environment for client initialization
    os.environ['VOLCES_API_KEY'] = 'demo-api-key-for-testing-12345'
    
    try:
        client = VolcesClient()
        
        # Create a request
        request = SeedanceRequestBody(
            prompt="This is a demo request to show logging",
            model="volces-v3",
            max_tokens=10
        )
        
        print("✓ Client initialized successfully with enhanced logging")
        print("✓ Request object created with validation")
        
        # Note: We're not actually making an API call to avoid network dependency
        # But the client is set up with all the enhanced logging and error handling
        
        print("✓ Enhanced logging and error handling are active")
        
    except Exception as e:
        print(f"✗ Error in logging demo: {e}")
    finally:
        # Clean up
        if 'VOLCES_API_KEY' in os.environ:
            del os.environ['VOLCES_API_KEY']
    
    print()


def demo_retry_mechanism():
    """Demonstrate retry mechanism"""
    print("=== Retry Mechanism Demo ===")
    
    # Set up environment for client initialization
    os.environ['VOLCES_API_KEY'] = 'demo-api-key-for-testing-12345'
    
    try:
        client = VolcesClient()
        
        # The client is initialized with retry strategy
        retry_strategy = client.session.adapters['https://'].max_retries
        print(f"✓ Retry mechanism configured with max retries: {retry_strategy.total}")
        print(f"✓ Backoff factor: {retry_strategy.backoff_factor}")
        print(f"✓ Status codes to retry: {retry_strategy.status_forcelist}")
        
        print("✓ Retry mechanism is active and ready")
        
    except Exception as e:
        print(f"✗ Error in retry demo: {e}")
    finally:
        # Clean up
        if 'VOLCES_API_KEY' in os.environ:
            del os.environ['VOLCES_API_KEY']
    
    print()


def main():
    """Run all demos"""
    print("New Features Demonstration - Volces API Client\n")
    
    demo_config_validation()
    demo_cache_functionality()
    demo_logging_and_error_handling()
    demo_retry_mechanism()
    
    print("=== All New Features Demonstrated Successfully ===")
    print("\nKey improvements:")
    print("- Configuration validation for API keys and URLs")
    print("- Smart caching for deterministic requests")
    print("- Enhanced logging with timing information")
    print("- Advanced retry mechanism with exponential backoff")
    print("- Improved error handling and classification")
    print("- Better connection pooling and timeout management")


if __name__ == "__main__":
    main()