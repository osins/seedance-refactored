"""Complex error classification and handling for API requests"""

import logging
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
from typing import Dict, Any, Optional
from ..model.response_body import SeedanceResponseBody
from ..utils.enums import APIErrorType


class ErrorHandling:
    """Handle complex error classification and processing"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def classify_error(self, e: Exception) -> APIErrorType:
        """
        Classify an exception into an appropriate error type.
        
        Args:
            e: Exception to classify
            
        Returns:
            Appropriate APIErrorType
        """
        if isinstance(e, ValueError):
            return APIErrorType.VALIDATION_ERROR
        elif isinstance(e, ConnectionError):
            return APIErrorType.NETWORK_ERROR
        elif isinstance(e, Timeout):
            return APIErrorType.NETWORK_ERROR
        elif isinstance(e, HTTPError):
            status_code = getattr(e.response, 'status_code', None)
            if status_code == 401:
                return APIErrorType.AUTHENTICATION_ERROR
            elif status_code == 429:
                return APIErrorType.RATE_LIMIT_ERROR
            elif status_code in [500, 502, 503, 504]:
                return APIErrorType.SERVER_ERROR
            else:
                return APIErrorType.VALIDATION_ERROR
        else:
            return APIErrorType.NETWORK_ERROR

    def handle_request_exception(self, e: RequestException, operation: str = "") -> SeedanceResponseBody:
        """
        Handle request exceptions with detailed error information.
        
        Args:
            e: Request exception to handle
            operation: Name of the operation that failed
            
        Returns:
            Error response object
        """
        self.logger.error(f"Request error during {operation}: {str(e)}")

        error_details = ""
        status_code = None
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.text
                status_code = e.response.status_code
            except Exception:
                error_details = str(getattr(e.response, 'text', ''))

        # Determine error type based on the exception
        error_type = self.classify_error(e)

        return SeedanceResponseBody(
            error={
                "type": error_type.value,
                "message": str(e),
                "details": error_details,
                "status_code": status_code
            }
        )

    def handle_general_exception(self, e: Exception, operation: str = "") -> SeedanceResponseBody:
        """
        Handle general exceptions.
        
        Args:
            e: Exception to handle
            operation: Name of the operation that failed
            
        Returns:
            Error response object
        """
        self.logger.error(f"General error during {operation}: {str(e)}")

        error_type = self.classify_error(e)

        return SeedanceResponseBody(
            error={
                "type": error_type.value if isinstance(e, ValueError) else "unknown_error",
                "message": str(e)
            }
        )

    def log_error_context(self, error_info: Dict[str, Any], context: Dict[str, Any] = None):
        """
        Log error with additional context information.
        
        Args:
            error_info: Dictionary containing error information
            context: Additional context to log with the error
        """
        log_msg = f"API Error: {error_info.get('type', 'unknown')} - {error_info.get('message', 'No message')}"
        if context:
            log_msg += f" | Context: {context}"
        self.logger.error(log_msg)

    def should_retry_error(self, error_response: SeedanceResponseBody) -> bool:
        """
        Determine if an error response indicates a retry should be attempted.
        
        Args:
            error_response: Error response from API
            
        Returns:
            True if the error suggests a retry, False otherwise
        """
        error_info = error_response.error
        if not error_info:
            return False

        status_code = error_info.get('status_code')
        error_type = error_info.get('type')

        # Retry on server errors and rate limit errors
        if status_code in [500, 502, 503, 504] or error_type == APIErrorType.RATE_LIMIT_ERROR.value:
            return True

        return False