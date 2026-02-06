"""Test script to verify imports work correctly"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from seedance.v3.models import SeedanceRequestBody, SeedanceResponseBody
    print("Models imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import method...")
    
    # Alternative approach - use the correct package structure
    import importlib.util
    
    # Load models module
    models_spec = importlib.util.spec_from_file_location(
        "models", 
        os.path.join(os.path.dirname(__file__), "src", "seedance", "v3", "models.py")
    )
    models_module = importlib.util.module_from_spec(models_spec)
    models_spec.loader.exec_module(models_module)
    
    # Access the classes
    SeedanceRequestBody = models_module.SeedanceRequestBody
    SeedanceResponseBody = models_module.SeedanceResponseBody
    print("Models imported successfully using alternative method")

# Test that we can create instances
try:
    request = SeedanceRequestBody(prompt="Test prompt", model="volces-v3")
    print("SeedanceRequestBody created successfully")
    print(f"Request: {request}")
except Exception as e:
    print(f"Error creating request: {e}")

try:
    response = SeedanceResponseBody(id="test-id", model="volces-v3")
    print("SeedanceResponseBody created successfully")
    print(f"Response: {response}")
except Exception as e:
    print(f"Error creating response: {e}")