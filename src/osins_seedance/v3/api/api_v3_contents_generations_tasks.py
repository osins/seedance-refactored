"""API Business Logic for /api/v3/contents/generations/tasks endpoint - Video Generation"""

import os
import time
from typing import Optional
from ..model.video_generation_request_body import VideoGenerationRequestBody
from ..model.video_generation_response_body import VideoGenerationResponseBody
from ..client.volces_client import VolcesClient
from ..utils.common_utils import load_environment_variables, setup_logging
import logging


# Load environment variables from .env file
load_environment_variables()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def seed_generations_tasks(request_body: VideoGenerationRequestBody) -> VideoGenerationResponseBody:
    """
    Generate video content using the Volces API with the given request body.
    This function implements the business logic for /api/v3/contents/generations/tasks endpoint.

    Args:
        request_body: Request body containing parameters for the video generation task

    Returns:
        Response body from the API with task ID
    """
    # Create a client instance
    client = VolcesClient()

    try:
        # Log the API call
        text_content = next((item.text for item in request_body.content if item.type == "text"), "No text content")
        logger.info(f"Making video generations tasks API call with model: {request_body.model}, text: {text_content[:50]}{'...' if len(text_content) > 50 else ''}")

        start_time = time.time()

        # Call the API using the client's video generation method
        response = client.call_video_generation_api(request_body)

        duration = time.time() - start_time
        logger.info(f"Video generations tasks API call completed in {duration:.2f}s")

        return response

    finally:
        # Clean up resources
        client.close()


def get_seedance_models() -> VideoGenerationResponseBody:
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