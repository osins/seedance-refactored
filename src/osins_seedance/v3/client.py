"""API Functions for Volces API v3"""

import os
import time
import requests
from dotenv import load_dotenv
from .models import SeedanceRequestBody, SeedanceResponseBody
from .utils import get_v3_api_base_url
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
VOLCES_API_KEY = os.getenv("VOLCES_API_KEY")
# Get base URL for v3 API using centralized function
BASE_URL = get_v3_api_base_url()  # Version path is fixed for v3 API


def _get_auth_headers() -> dict:
    """
    Helper function to get authorization headers.

    Returns:
        Dictionary containing authorization headers

    Raises:
        ValueError: If VOLCES_API_KEY is not set
    """
    if not VOLCES_API_KEY:
        raise ValueError("VOLCES_API_KEY environment variable is not set")

    return {
        "Authorization": f"Bearer {VOLCES_API_KEY}",
        "Content-Type": "application/json"
    }


def _handle_request_exception(e: requests.exceptions.RequestException) -> SeedanceResponseBody:
    """
    Helper function to handle request exceptions.

    Args:
        e: The request exception to handle

    Returns:
        Error response object
    """
    logger.error(f"Request error: {str(e)}")

    error_details = ""
    if hasattr(e, 'response') and e.response is not None:
        try:
            error_details = e.response.text
        except Exception:
            error_details = str(getattr(e.response, 'text', ''))

    return SeedanceResponseBody(
        error={
            "type": "request_error",
            "message": str(e),
            "details": error_details,
            "status_code": e.response.status_code if hasattr(e, 'response') and e.response else None
        }
    )


def _handle_general_exception(e: Exception) -> SeedanceResponseBody:
    """
    Helper function to handle general exceptions.

    Args:
        e: The exception to handle

    Returns:
        Error response object
    """
    logger.error(f"General error: {str(e)}")

    return SeedanceResponseBody(
        error={
            "type": "unknown_error",
            "message": str(e)
        }
    )


def seed_generations_tasks(request_body: SeedanceRequestBody) -> SeedanceResponseBody:
    """
    Generate content using the Volces API with the given request body.

    Args:
        request_body: Request body containing parameters for the generation task

    Returns:
        Response body from the API
    """
    # Log the API call
    logger.info(f"Making API call with prompt: {request_body.prompt[:50]}{'...' if len(request_body.prompt) > 50 else ''}")

    start_time = time.time()

    try:
        headers = _get_auth_headers()

        response = requests.post(
            f"{BASE_URL}/generate",  # Path already includes /v3 from BASE_URL
            headers=headers,
            json=request_body.model_dump(),
            timeout=30
        )

        duration = time.time() - start_time
        logger.info(f"API call completed in {duration:.2f}s with status {response.status_code}")

        response.raise_for_status()

        # Parse response JSON
        response_json = response.json()

        # Return as response model
        return SeedanceResponseBody(**response_json)

    except requests.exceptions.HTTPError as e:
        duration = time.time() - start_time
        logger.error(f"API call failed after {duration:.2f}s with HTTP error: {str(e)}")
        return _handle_request_exception(e)
    except requests.exceptions.ConnectionError as e:
        duration = time.time() - start_time
        logger.error(f"API call failed after {duration:.2f}s with connection error: {str(e)}")
        return _handle_request_exception(e)
    except requests.exceptions.Timeout as e:
        duration = time.time() - start_time
        logger.error(f"API call failed after {duration:.2f}s with timeout: {str(e)}")
        return _handle_request_exception(e)
    except requests.exceptions.RequestException as e:
        duration = time.time() - start_time
        logger.error(f"API call failed after {duration:.2f}s with request error: {str(e)}")
        return _handle_request_exception(e)
    except ValueError as e:
        # Handle JSON decode errors
        duration = time.time() - start_time
        logger.error(f"API call failed after {duration:.2f}s with JSON decode error: {str(e)}")
        return _handle_general_exception(e)
    except Exception as e:
        # Handle other unexpected errors
        duration = time.time() - start_time
        logger.error(f"API call failed after {duration:.2f}s with unexpected error: {str(e)}")
        return _handle_general_exception(e)


def get_seedance_models() -> SeedanceResponseBody:
    """
    Get available models from Volces API.

    Returns:
        Response body containing available models
    """
    logger.info(f"Fetching models from {BASE_URL}/models")

    start_time = time.time()

    try:
        headers = _get_auth_headers()

        response = requests.get(
            f"{BASE_URL}/models",  # Path already includes /v3 from BASE_URL
            headers=headers,
            timeout=30
        )

        duration = time.time() - start_time
        logger.info(f"Models fetch completed in {duration:.2f}s with status {response.status_code}")

        response.raise_for_status()

        # Parse response JSON
        response_json = response.json()

        # Return as response model
        return SeedanceResponseBody(**response_json)

    except requests.exceptions.HTTPError as e:
        duration = time.time() - start_time
        logger.error(f"Models fetch failed after {duration:.2f}s with HTTP error: {str(e)}")
        return _handle_request_exception(e)
    except requests.exceptions.ConnectionError as e:
        duration = time.time() - start_time
        logger.error(f"Models fetch failed after {duration:.2f}s with connection error: {str(e)}")
        return _handle_request_exception(e)
    except requests.exceptions.Timeout as e:
        duration = time.time() - start_time
        logger.error(f"Models fetch failed after {duration:.2f}s with timeout: {str(e)}")
        return _handle_request_exception(e)
    except requests.exceptions.RequestException as e:
        duration = time.time() - start_time
        logger.error(f"Models fetch failed after {duration:.2f}s with request error: {str(e)}")
        return _handle_request_exception(e)
    except ValueError as e:
        # Handle JSON decode errors
        duration = time.time() - start_time
        logger.error(f"Models fetch failed after {duration:.2f}s with JSON decode error: {str(e)}")
        return _handle_general_exception(e)
    except Exception as e:
        # Handle other unexpected errors
        duration = time.time() - start_time
        logger.error(f"Models fetch failed after {duration:.2f}s with unexpected error: {str(e)}")
        return _handle_general_exception(e)