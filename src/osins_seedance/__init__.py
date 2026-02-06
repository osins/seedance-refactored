"""Osins-Seedance API Package"""

# Import v3 modules to make them accessible at package level
from .v3 import seed_generations_tasks, get_seedance_models

__version__ = "3.0.0"
__all__ = ["seed_generations_tasks", "get_seedance_models"]