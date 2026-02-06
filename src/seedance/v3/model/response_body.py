"""Response body model for Volces API v3 with strict validation"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict
import re


class SeedanceResponseBody(BaseModel):
    """Response body model for Volces API calls with strict validation"""

    # Standard API response fields
    id: Optional[str] = Field(default=None, pattern=r'^[\w\-_.]+$', description="Unique identifier for the response")
    object: Optional[str] = Field(default=None, description="Type of the response object")
    created: Optional[int] = Field(default=None, ge=0, description="Unix timestamp of creation")
    model: Optional[str] = Field(default=None, description="Model used for the response")
    choices: Optional[List[Dict[str, Any]]] = Field(default=None, max_length=10, description="List of generated choices")
    usage: Optional[Dict[str, Any]] = Field(default=None, description="Usage statistics")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error information if any")

    @field_validator('id')
    @classmethod
    def validate_id(cls, v):
        if v is not None:
            # Validate ID format (alphanumeric, hyphens, underscores, dots)
            if not re.match(r'^[\w\-_.]+$', v):
                raise ValueError('ID can only contain alphanumeric characters, hyphens, underscores, and dots')
        return v

    model_config = ConfigDict(
        # Allow extra fields in case API returns additional data
        extra="allow",
        # Strict validation
        validate_assignment=True
    )