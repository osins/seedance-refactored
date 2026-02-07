#!/usr/bin/env python3
"""
Test script to validate the video generation API models against the documentation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.osins_seedance.v3.model.video_generation_request_body import (
    VideoGenerationRequestBody, 
    TextContent, 
    ImageUrlObject, 
    ImageContent, 
    DraftTaskObject, 
    DraftTaskContent
)
from src.osins_seedance.v3.utils.validation_utils import VideoGenerationValidator


def test_basic_text_generation():
    """Test basic text-to-video generation"""
    print("Testing basic text-to-video generation...")
    
    request_body = VideoGenerationRequestBody(
        model="doubao-seedance-1-5-pro-251215",
        content=[
            {
                "type": "text",
                "text": "A cat playing with a ball of yarn"
            }
        ],
        resolution="720p",
        ratio="16:9",
        duration=5,
        seed=42
    )
    
    validation_result = VideoGenerationValidator.comprehensive_validation(request_body)
    
    print(f"Valid: {validation_result['valid']}")
    if not validation_result['valid']:
        print(f"Errors: {validation_result['errors']}")
    else:
        print("✓ Basic text generation test passed")
    
    return validation_result['valid']


def test_image_to_video_first_frame():
    """Test image-to-video with first frame"""
    print("\nTesting image-to-video with first frame...")
    
    request_body = VideoGenerationRequestBody(
        model="doubao-seedance-1-0-pro",
        content=[
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/image.jpg"},
                "role": "first_frame"
            },
            {
                "type": "text",
                "text": "A continuation of the scene in the image"
            }
        ],
        resolution="720p",
        duration=5
    )
    
    validation_result = VideoGenerationValidator.comprehensive_validation(request_body)
    
    print(f"Valid: {validation_result['valid']}")
    if not validation_result['valid']:
        print(f"Errors: {validation_result['errors']}")
    else:
        print("✓ Image-to-video first frame test passed")
    
    return validation_result['valid']


def test_image_to_video_first_last_frame():
    """Test image-to-video with first and last frame"""
    print("\nTesting image-to-video with first and last frame...")
    
    request_body = VideoGenerationRequestBody(
        model="doubao-seedance-1-5-pro-251215",
        content=[
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/first_frame.jpg"},
                "role": "first_frame"
            },
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/last_frame.jpg"},
                "role": "last_frame"
            },
            {
                "type": "text",
                "text": "A smooth transition between the two images"
            }
        ],
        resolution="720p",
        duration=5
    )
    
    validation_result = VideoGenerationValidator.comprehensive_validation(request_body)
    
    print(f"Valid: {validation_result['valid']}")
    if not validation_result['valid']:
        print(f"Errors: {validation_result['errors']}")
    else:
        print("✓ Image-to-video first-last frame test passed")
    
    return validation_result['valid']


def test_reference_images():
    """Test reference image generation"""
    print("\nTesting reference image generation...")
    
    request_body = VideoGenerationRequestBody(
        model="doubao-seedance-1-0-lite-i2v",
        content=[
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/ref1.jpg"},
                "role": "reference_image"
            },
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/ref2.jpg"},
                "role": "reference_image"
            },
            {
                "type": "text",
                "text": "A scene inspired by the reference images"
            }
        ],
        resolution="720p",
        duration=5
    )
    
    validation_result = VideoGenerationValidator.comprehensive_validation(request_body)
    
    print(f"Valid: {validation_result['valid']}")
    if not validation_result['valid']:
        print(f"Errors: {validation_result['errors']}")
    else:
        print("✓ Reference image test passed")
    
    return validation_result['valid']


def test_invalid_combinations():
    """Test invalid content combinations"""
    print("\nTesting invalid content combinations...")
    
    # This should fail - mixing first_frame with reference_image
    try:
        request_body = VideoGenerationRequestBody(
            model="doubao-seedance-1-5-pro-251215",
            content=[
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/first.jpg"},
                    "role": "first_frame"
                },
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/ref.jpg"},
                    "role": "reference_image"
                },
                {
                    "type": "text",
                    "text": "This should fail due to mixed roles"
                }
            ]
        )
        
        # If we reach here, the validation didn't catch the error
        print("✗ Expected this to fail but it passed")
        return False
    except Exception as e:
        print(f"Expected failure - Exception caught: {str(e)}")
        print("✓ Invalid combination correctly detected")
        return True


def test_draft_task():
    """Test draft task functionality"""
    print("\nTesting draft task functionality...")
    
    request_body = VideoGenerationRequestBody(
        model="doubao-seedance-1-5-pro-251215",
        content=[
            {
                "type": "draft_task",
                "draft_task": {"id": "draft-task-12345"}
            }
        ],
        resolution="720p",
        duration=5
    )
    
    validation_result = VideoGenerationValidator.comprehensive_validation(request_body)
    
    print(f"Valid: {validation_result['valid']}")
    if not validation_result['valid']:
        print(f"Errors: {validation_result['errors']}")
    else:
        print("✓ Draft task test passed")
    
    return validation_result['valid']


def test_parameter_validation():
    """Test parameter validation"""
    print("\nTesting parameter validation...")
    
    request_body = VideoGenerationRequestBody(
        model="doubao-seedance-1-5-pro-251215",
        content=[
            {
                "type": "text",
                "text": "A test video"
            }
        ],
        resolution="720p",
        ratio="16:9",
        duration=5,
        frames=121,  # 25 + 4*24 = 121, should be valid
        seed=12345,
        camera_fixed=False,
        watermark=True,
        service_tier="default",
        execution_expires_after=86400,  # 24 hours
        generate_audio=True,
        draft=False
    )
    
    validation_result = VideoGenerationValidator.comprehensive_validation(request_body)
    
    print(f"Valid: {validation_result['valid']}")
    if not validation_result['valid']:
        print(f"Errors: {validation_result['errors']}")
    else:
        print("✓ Parameter validation test passed")
    
    return validation_result['valid']


def main():
    """Run all tests"""
    print("Running video generation API model validation tests...\n")
    
    tests = [
        test_basic_text_generation,
        test_image_to_video_first_frame,
        test_image_to_video_first_last_frame,
        test_reference_images,
        test_invalid_combinations,
        test_draft_task,
        test_parameter_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Models are correctly implemented according to API documentation.")
        return True
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)