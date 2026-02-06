"""Error handling utilities for API requests"""

import logging
from requests.exceptions import RequestException
from typing import Dict, Any
from ..model.response_body import SeedanceResponseBody
from .enums import APIErrorType


def handle_request_exception(e: RequestException, operation: str = "") -> SeedanceResponseBody:
    """Helper function to handle request exceptions."""
    logger = logging.getLogger(__name__)
    logger.error(f"Request error during {operation}: {str(e)}")

    error_details = ""
    status_code = None
    if hasattr(e, 'response') and e.response is not None:
        try:
            error_details = e.response.text
            status_code = e.response.status_code
        except Exception:
            error_details = str(getattr(e.response, 'text', ''))

    # Determine error type based on the exception
    error_type = APIErrorType.NETWORK_ERROR
    if status_code == 401 or "authentication" in str(e).lower():
        error_type = APIErrorType.AUTHENTICATION_ERROR
    elif status_code in [500, 502, 503, 504]:
        error_type = APIErrorType.SERVER_ERROR
    elif status_code == 429:
        error_type = APIErrorType.RATE_LIMIT_ERROR

    return SeedanceResponseBody(
        error={
            "type": error_type.value,
            "message": str(e),
            "details": error_details,
            "status_code": status_code
        }
    )


def handle_general_exception(e: Exception, operation: str = "") -> SeedanceResponseBody:
    """Helper function to handle general exceptions."""
    logger = logging.getLogger(__name__)
    logger.error(f"General error during {operation}: {str(e)}")

    return SeedanceResponseBody(
        error={
            "type": APIErrorType.VALIDATION_ERROR.value if isinstance(e, ValueError) else "unknown_error",
            "message": str(e)
        }
    )