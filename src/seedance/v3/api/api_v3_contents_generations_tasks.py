"""API Business Logic for /api/v3/contents/generations/tasks endpoint"""

import os
import time
from typing import Optional
from ..model.request_body import SeedanceRequestBody
from ..model.response_body import SeedanceResponseBody
from ..client.volces_client import VolcesClient
from ..utils.common_utils import load_environment_variables, setup_logging
import logging


# Load environment variables from .env file
load_environment_variables()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def seed_generations_tasks(request_body: SeedanceRequestBody) -> SeedanceResponseBody:
    """
    Generate content using the Volces API with the given request body.
    This function implements the business logic for /api/v3/contents/generations/tasks endpoint.

    Args:
        request_body: Request body containing parameters for the generation task

    Returns:
        Response body from the API
    """
    # Create a client instance
    client = VolcesClient()
    
    try:
        # Log the API call
        logger.info(f"Making generations tasks API call with prompt: {request_body.prompt[:50]}{'...' if len(request_body.prompt) > 50 else ''}")

        start_time = time.time()

        # Call the API using the client
        response = client.call_volces_api(request_body)

        duration = time.time() - start_time
        logger.info(f"Generations tasks API call completed in {duration:.2f}s")

        return response

    finally:
        # Clean up resources
        client.close()


def get_seedance_models() -> SeedanceResponseBody:
    """
    Get available models from Volces API.
    This function could be associated with a models endpoint.

    Returns:
        Response body containing available models
    """
    # Create a client instance
    client = VolcesClient()
    
    try:
        start_time = time.time()

        # Get models using the client
        response = client.get_volces_models()

        duration = time.time() - start_time
        logger.info(f"Models fetch completed in {duration:.2f}s")

        return response

    finally:
        # Clean up resources
        client.close()