"""Request body model for Volces API v3 with strict validation"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict
import re


class SeedanceRequestBody(BaseModel):
    """Request body model for Volces API calls with strict validation"""

    # Required fields
    prompt: str = Field(..., min_length=1, max_length=10000, description="Input prompt for the API")

    # Optional fields with validation
    model: Optional[str] = Field(default=None, pattern=r'^[\w\-_.]+$', description="Model identifier")
    max_tokens: Optional[int] = Field(default=100, ge=1, le=10000, description="Maximum number of tokens to generate")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0, description="Top-p sampling parameter")
    n: Optional[int] = Field(default=1, ge=1, le=10, description="Number of completions to generate")
    stream: Optional[bool] = Field(default=False, description="Whether to stream the response")
    stop: Optional[List[str]] = Field(default=None, max_length=4, description="Sequences where generation should stop")
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0, description="Penalty for new tokens based on presence")
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0, description="Penalty for new tokens based on frequency")
    logit_bias: Optional[Dict[str, float]] = Field(default=None, description="Modify likelihood of specified tokens")
    user: Optional[str] = Field(default=None, min_length=1, max_length=256, description="User identifier")

    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError('Prompt cannot be empty or just whitespace')
        return v.strip()

    @field_validator('model')
    @classmethod
    def validate_model(cls, v):
        if v is not None:
            # Validate model name format (alphanumeric, hyphens, underscores, dots)
            if not re.match(r'^[\w\-_.]+$', v):
                raise ValueError('Model name can only contain alphanumeric characters, hyphens, underscores, and dots')
        return v

    @field_validator('stop')
    @classmethod
    def validate_stop_sequences(cls, v):
        if v is not None:
            if len(v) > 4:  # Limit the number of stop sequences
                raise ValueError('Maximum of 4 stop sequences allowed')
            for seq in v:
                if len(seq) > 100:
                    raise ValueError('Stop sequences must be less than 100 characters')
        return v

    model_config = ConfigDict(
        # Allow extra fields in case API adds new parameters
        extra="allow",
        # Strict validation
        validate_assignment=True
    )