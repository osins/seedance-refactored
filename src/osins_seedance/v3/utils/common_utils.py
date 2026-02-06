"""Common utility functions"""

import logging
from dotenv import load_dotenv
import os


def setup_logging():
    """Configure logging for the module"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def load_environment_variables():
    """Load environment variables from .env file"""
    load_dotenv()


def get_api_key() -> str:
    """Get API key from environment variable"""
    api_key = os.getenv("VOLCES_API_KEY")
    if not api_key:
        raise ValueError("VOLCES_API_KEY environment variable is not set")
    return api_key