"""Validation utilities for video generation API models"""

from typing import Dict, Any, List
from ..model.video_generation_request_body import VideoGenerationRequestBody, ContentItem, TextContent, ImageContent, DraftTaskContent
import re


class ConfigValidator:
    """Configuration validator to ensure valid parameters"""

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format and presence"""
        if not api_key:
            raise ValueError("API key is required")
        if not isinstance(api_key, str) or len(api_key) < 10:  # Realistic minimum length
            raise ValueError("Invalid API key format - must be at least 10 characters")
        return True

    @staticmethod
    def validate_base_url(base_url: str) -> bool:
        """Validate base URL format"""
        if not base_url.startswith(('http://', 'https://')):
            raise ValueError("Base URL must start with http:// or https://")
        return True


class VideoGenerationValidator:
    """Validation utilities for video generation API models"""
    
    @staticmethod
    def validate_content_combinations(request_body: VideoGenerationRequestBody) -> Dict[str, Any]:
        """
        Validate content combinations according to API documentation rules
        
        According to the API docs:
        -首帧图生视频、首尾帧图生视频、参考图生视频为 3 种互斥的场景，不支持混用
        - Only one draft_task content item is allowed
        - draft_task cannot be combined with other content types
        """
        errors = []
        
        # Count different content types
        text_count = sum(1 for item in request_body.content if isinstance(item, TextContent))
        image_count = sum(1 for item in request_body.content if isinstance(item, ImageContent))
        draft_task_count = sum(1 for item in request_body.content if isinstance(item, DraftTaskContent))
        
        # Validate draft_task rules
        if draft_task_count > 1:
            errors.append('Only one draft_task content item is allowed')
        
        if draft_task_count == 1 and (text_count > 0 or image_count > 0):
            errors.append('draft_task cannot be combined with other content types')
        
        # Validate image roles if present
        if image_count > 0:
            image_items = [item for item in request_body.content if isinstance(item, ImageContent)]
            roles = [item.role for item in image_items if item.role is not None]
            
            # Check for conflicting roles
            has_first_frame = "first_frame" in roles
            has_last_frame = "last_frame" in roles
            has_reference_image = "reference_image" in roles
            
            # Validate mutually exclusive roles
            if has_first_frame and has_reference_image:
                errors.append('first_frame and reference_image roles cannot be mixed (mutually exclusive)')
            
            # Validate first_frame/last_frame combination rules
            first_frame_roles = [role for role in roles if role == "first_frame"]
            last_frame_roles = [role for role in roles if role == "last_frame"]
            reference_image_roles = [role for role in roles if role == "reference_image"]
            
            if len(first_frame_roles) > 1:
                errors.append('Only one first_frame image is allowed')
            
            if len(last_frame_roles) > 1:
                errors.append('Only one last_frame image is allowed')
            
            if len(first_frame_roles) == 0 and len(last_frame_roles) > 0:
                errors.append('last_frame requires a corresponding first_frame')
            
            # Validate reference image count limits (1-4 for reference images)
            if len(reference_image_roles) > 4:
                errors.append('Reference images are limited to 1-4 images')
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "summary": {
                "text_content_count": text_count,
                "image_content_count": image_count,
                "draft_task_count": draft_task_count
            }
        }
    
    @staticmethod
    def validate_video_parameters(request_body: VideoGenerationRequestBody) -> Dict[str, Any]:
        """
        Validate video-specific parameters according to API documentation
        """
        errors = []
        
        # Validate duration
        if request_body.duration is not None:
            if request_body.duration != -1 and (request_body.duration < 2 or request_body.duration > 12):
                errors.append('Duration must be -1 or between 2 and 12 seconds')
        
        # Validate frames (only for non-1.5 pro models, but we'll validate the pattern anyway)
        if request_body.frames is not None:
            if request_body.frames < 29 or request_body.frames > 289:
                errors.append('Frames must be between 29 and 289')
            
            if (request_body.frames - 25) % 4 != 0:
                errors.append('Frames must follow the pattern 25 + 4n where n is a positive integer')
        
        # Validate seed range
        if request_body.seed is not None:
            if request_body.seed < -1 or request_body.seed > 4294967295:  # 2^32 - 1
                errors.append('Seed must be between -1 and 2^32-1')
        
        # Validate resolution
        if request_body.resolution is not None:
            valid_resolutions = ["480p", "720p", "1080p"]
            if request_body.resolution not in valid_resolutions:
                errors.append(f'Resolution must be one of {valid_resolutions}')
        
        # Validate ratio
        if request_body.ratio is not None:
            valid_ratios = ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"]
            if request_body.ratio not in valid_ratios:
                errors.append(f'Ratio must be one of {valid_ratios}')
        
        # Validate service tier
        if request_body.service_tier is not None:
            valid_tiers = ["default", "flex"]
            if request_body.service_tier not in valid_tiers:
                errors.append(f'Service tier must be one of {valid_tiers}')
        
        # Validate execution_expires_after
        if request_body.execution_expires_after is not None:
            if request_body.execution_expires_after < 3600 or request_body.execution_expires_after > 259200:
                errors.append('Execution expires after must be between 3600 and 259200 seconds')
        
        # Validate camera_fixed with reference images (should not be used together)
        if request_body.camera_fixed is not None and request_body.camera_fixed:
            image_items = [item for item in request_body.content if isinstance(item, ImageContent)]
            has_reference_images = any(item.role == "reference_image" for item in image_items)
            if has_reference_images:
                errors.append('camera_fixed parameter is not supported with reference images')
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def validate_model_compatibility(request_body: VideoGenerationRequestBody) -> Dict[str, Any]:
        """
        Validate model-specific compatibility rules based on API documentation
        """
        errors = []
        warnings = []
        
        model_name = request_body.model.lower()
        
        # Check for model-specific features
        if "1-5-pro" in model_name or "1.5" in model_name:
            # Seedance 1.5 pro specific validations
            if request_body.generate_audio is not None:
                # This is valid for 1.5 pro
                pass
            if request_body.draft is not None:
                # This is valid for 1.5 pro
                pass
        else:
            # For non-1.5 pro models, certain features may not be supported
            if request_body.generate_audio is False:  # If explicitly set to False
                warnings.append(f'Model {model_name} may not support generate_audio parameter')
            if request_body.draft:
                warnings.append(f'Model {model_name} may not support draft mode')
        
        # Check for lite model limitations
        if "lite" in model_name:
            # Lite models have specific limitations
            if request_body.resolution == "1080p":
                image_items = [item for item in request_body.content if isinstance(item, ImageContent)]
                has_reference_images = any(item.role == "reference_image" for item in image_items)
                if has_reference_images:
                    errors.append(f'Model {model_name} (lite) does not support 1080p resolution with reference images')
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def comprehensive_validation(request_body: VideoGenerationRequestBody) -> Dict[str, Any]:
        """
        Perform comprehensive validation of the request body
        """
        content_validation = VideoGenerationValidator.validate_content_combinations(request_body)
        parameter_validation = VideoGenerationValidator.validate_video_parameters(request_body)
        compatibility_validation = VideoGenerationValidator.validate_model_compatibility(request_body)
        
        all_errors = (
            content_validation["errors"] + 
            parameter_validation["errors"] + 
            compatibility_validation["errors"]
        )
        
        all_warnings = compatibility_validation["warnings"]
        
        return {
            "valid": len(all_errors) == 0,
            "errors": all_errors,
            "warnings": all_warnings,
            "details": {
                "content_validation": content_validation,
                "parameter_validation": parameter_validation,
                "compatibility_validation": compatibility_validation
            }
        }


def validate_video_generation_request(request_body: VideoGenerationRequestBody) -> bool:
    """
    Convenience function to validate a video generation request
    Returns True if valid, False otherwise
    """
    result = VideoGenerationValidator.comprehensive_validation(request_body)
    return result["valid"]