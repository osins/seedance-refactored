#!/usr/bin/env python3
"""
Example usage of the Seedance video generation API
Demonstrates various video generation scenarios based on the API documentation
"""

import os
import sys
from typing import Optional

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from osins_seedance import (
    VideoGenerationRequestBody,
    seed_generations_tasks
)


def example_text_to_video():
    """Example: Text-to-video generation"""
    print("=== Text-to-Video Generation Example ===")
    
    request_body = VideoGenerationRequestBody(
        model="doubao-seedance-1-5-pro-251215",
        content=[
            {
                "type": "text",
                "text": "A beautiful sunset over mountains with clouds moving slowly"
            }
        ],
        resolution="720p",
        ratio="16:9",
        duration=5,
        seed=12345,
        generate_audio=True,  # Only supported in 1.5 pro
        watermark=False
    )
    
    print(f"Request: {request_body.model_dump()}")
    print("This would generate a video based on the text prompt...")
    print()


def example_image_to_video_first_frame():
    """Example: Image-to-video with first frame"""
    print("=== Image-to-Video (First Frame) Example ===")
    
    request_body = VideoGenerationRequestBody(
        model="doubao-seedance-1-0-pro",
        content=[
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/landscape.jpg"},
                "role": "first_frame"
            },
            {
                "type": "text",
                "text": "Continue the scene showing the landscape coming alive with animals appearing"
            }
        ],
        resolution="720p",
        duration=6,
        seed=67890
    )
    
    print(f"Request: {request_body.model_dump()}")
    print("This would generate a video starting from the provided image...")
    print()


def example_image_to_video_first_last_frame():
    """Example: Image-to-video with first and last frame"""
    print("=== Image-to-Video (First & Last Frame) Example ===")
    
    request_body = VideoGenerationRequestBody(
        model="doubao-seedance-1-5-pro-251215",
        content=[
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/scene_start.jpg"},
                "role": "first_frame"
            },
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/scene_end.jpg"},
                "role": "last_frame"
            },
            {
                "type": "text",
                "text": "Smooth transition from start scene to end scene with natural movement"
            }
        ],
        resolution="1080p",
        ratio="16:9",
        duration=8,
        seed=54321,
        camera_fixed=False
    )
    
    print(f"Request: {request_body.model_dump()}")
    print("This would generate a video transitioning between the two images...")
    print()


def example_reference_images():
    """Example: Reference image-based video generation"""
    print("=== Reference Image Video Generation Example ===")
    
    request_body = VideoGenerationRequestBody(
        model="doubao-seedance-1-0-lite-i2v",
        content=[
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/reference1.jpg"},
                "role": "reference_image"
            },
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/reference2.jpg"},
                "role": "reference_image"
            },
            {
                "type": "text",
                "text": "[图1] A person wearing the outfit from reference 1 walking in the scene from [图2] reference 2"
            }
        ],
        resolution="720p",
        ratio="9:16",  # Vertical video for social media
        duration=5,
        seed=11111
    )
    
    print(f"Request: {request_body.model_dump()}")
    print("This would generate a video using the reference images as style guides...")
    print()


def example_draft_workflow():
    """Example: Draft workflow for video generation"""
    print("=== Draft Workflow Example ===")
    
    # Step 1: Create a draft video (quick preview)
    draft_request = VideoGenerationRequestBody(
        model="doubao-seedance-1-5-pro-251215",
        content=[
            {
                "type": "text",
                "text": "A futuristic cityscape with flying cars"
            }
        ],
        resolution="480p",  # Lower resolution for draft
        duration=5,
        draft=True,  # Enable draft mode for quick preview
        generate_audio=False  # No audio in draft
    )
    
    print(f"Draft Request: {draft_request.model_dump()}")
    print("This creates a low-resolution draft for quick preview...")
    
    # Step 2: Once satisfied with draft, generate final video using draft task ID
    final_request = VideoGenerationRequestBody(
        model="doubao-seedance-1-5-pro-251215",
        content=[
            {
                "type": "draft_task",
                "draft_task": {"id": "draft-task-abc123"}  # ID from draft response
            }
        ],
        resolution="1080p",  # Higher resolution for final
        duration=5,
        draft=False,  # Disable draft mode
        generate_audio=True  # Include audio in final
    )
    
    print(f"Final Request using draft: {final_request.model_dump()}")
    print("This generates the final high-quality video based on the draft...")
    print()


def example_with_callback():
    """Example: Video generation with callback URL"""
    print("=== Video Generation with Callback Example ===")
    
    request_body = VideoGenerationRequestBody(
        model="doubao-seedance-1-0-pro",
        content=[
            {
                "type": "text",
                "text": "Corporate presentation animation with logo transitions"
            }
        ],
        resolution="1080p",
        ratio="16:9",
        duration=10,  # Max 12 seconds
        seed=99999,
        callback_url="https://your-app.com/webhook/video-generation-complete",
        execution_expires_after=172800,  # 48 hours
        service_tier="default"  # Online inference
    )
    
    print(f"Request with callback: {request_body.model_dump()}")
    print("This would notify your webhook when generation completes...")
    print()


def example_return_last_frame():
    """Example: Video generation with last frame return"""
    print("=== Video Generation with Last Frame Return Example ===")
    
    request_body = VideoGenerationRequestBody(
        model="doubao-seedance-1-5-pro-251215",
        content=[
            {
                "type": "text",
                "text": "A flowing river with trees swaying in the wind"
            }
        ],
        resolution="720p",
        ratio="16:9",
        duration=5,
        return_last_frame=True,  # Request the last frame image
        generate_audio=True
    )
    
    print(f"Request with last frame: {request_body.model_dump()}")
    print("This would return both the video and the last frame image...")
    print("Useful for creating continuous videos by using last frame as next video's first frame.")
    print()


def main():
    """Run all examples"""
    print("Seedance Video Generation API Examples")
    print("=" * 50)
    print()
    
    example_text_to_video()
    example_image_to_video_first_frame()
    example_image_to_video_first_last_frame()
    example_reference_images()
    example_draft_workflow()
    example_with_callback()
    example_return_last_frame()
    
    print("For actual API calls, ensure you have:")
    print("1. Set VOLCES_API_KEY environment variable")
    print("2. Valid model ID from the Seedance model list")
    print("3. Properly formatted content objects")
    print()
    print("API Documentation References:")
    print("- Text-to-video: Generate video from text prompt")
    print("- Image-to-video: Use 1 image (first frame) or 2 images (first & last frame)")
    print("- Reference images: Use 1-4 reference images for style guidance")
    print("- Draft workflow: Create quick preview then generate final video")
    print("- Callbacks: Get notified when generation completes")
    print("- Last frame: Get the final frame for continuous video creation")


if __name__ == "__main__":
    main()