"""Request body model for Volces Video Generation API v3 with strict validation"""

from typing import Optional, List, Union, Literal
from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict
import re


class TextContent(BaseModel):
    """文本内容对象"""
    type: Literal["text"]
    text: str = Field(..., min_length=1, max_length=5000, description="输入给模型的文本内容，描述期望生成的视频")


class ImageUrlObject(BaseModel):
    """图片URL对象"""
    url: str = Field(..., min_length=1, max_length=2048, description="图片信息，可以是图片URL或图片Base64编码")


class ImageContent(BaseModel):
    """图片内容对象"""
    type: Literal["image_url"]
    image_url: ImageUrlObject
    role: Optional[Literal["first_frame", "last_frame", "reference_image"]] = Field(
        default=None, 
        description="图片的位置或用途：first_frame(首帧), last_frame(尾帧), reference_image(参考图)"
    )


class DraftTaskObject(BaseModel):
    """样片任务对象"""
    id: str = Field(..., min_length=1, max_length=128, description="样片任务ID")


class DraftTaskContent(BaseModel):
    """样片内容对象"""
    type: Literal["draft_task"]
    draft_task: DraftTaskObject


# Union type for content items
ContentItem = Union[TextContent, ImageContent, DraftTaskContent]


class VideoGenerationRequestBody(BaseModel):
    """视频生成任务请求体模型"""

    # Required fields
    model: str = Field(..., min_length=1, max_length=256, description="模型ID")
    content: List[ContentItem] = Field(..., min_length=1, max_length=10, description="输入给模型生成视频的信息")

    # Optional fields
    callback_url: Optional[str] = Field(
        default=None, 
        max_length=2048, 
        description="填写本次生成任务结果的回调通知地址"
    )
    
    return_last_frame: Optional[bool] = Field(
        default=False, 
        description="是否返回生成视频的尾帧图像"
    )
    
    service_tier: Optional[Literal["default", "flex"]] = Field(
        default="default", 
        description="服务等级：default(在线推理), flex(离线推理)"
    )
    
    execution_expires_after: Optional[int] = Field(
        default=172800, 
        ge=3600, 
        le=259200, 
        description="任务超时阈值，单位秒，取值范围[3600, 259200]"
    )
    
    generate_audio: Optional[bool] = Field(
        default=True, 
        description="是否生成音频，仅Seedance 1.5 pro支持"
    )
    
    draft: Optional[bool] = Field(
        default=False, 
        description="是否开启样片模式，仅Seedance 1.5 pro支持"
    )

    # Video parameters (optional)
    resolution: Optional[Literal["480p", "720p", "1080p"]] = Field(
        default=None, 
        description="视频分辨率"
    )
    
    ratio: Optional[Literal["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"]] = Field(
        default=None, 
        description="视频宽高比"
    )
    
    duration: Optional[int] = Field(
        default=None, 
        ge=-1, 
        le=12, 
        description="视频时长(秒)，支持2-12秒，-1表示由模型自主选择"
    )
    
    frames: Optional[int] = Field(
        default=None, 
        description="视频帧数，支持[29, 289]区间内满足25+4n格式的值"
    )
    
    seed: Optional[int] = Field(
        default=-1, 
        ge=-1, 
        le=4294967295,  # 2^32 - 1
        description="种子整数，用于控制生成内容的随机性"
    )
    
    camera_fixed: Optional[bool] = Field(
        default=False, 
        description="是否固定摄像头，参考图场景不支持"
    )
    
    watermark: Optional[bool] = Field(
        default=False, 
        description="生成视频是否包含水印"
    )

    @field_validator('model')
    @classmethod
    def validate_model(cls, v):
        if not v or not v.strip():
            raise ValueError('Model cannot be empty')
        return v.strip()

    @field_validator('callback_url')
    @classmethod
    def validate_callback_url(cls, v):
        if v is not None:
            # Basic URL validation
            if not v.startswith(('http://', 'https://')):
                raise ValueError('Callback URL must start with http:// or https://')
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Content must not be empty')
        
        # Count different content types
        text_count = sum(1 for item in v if item.type == "text")
        image_count = sum(1 for item in v if item.type == "image_url")
        draft_task_count = sum(1 for item in v if item.type == "draft_task")
        
        # Validate content combinations
        if draft_task_count > 1:
            raise ValueError('Only one draft_task content item is allowed')
        
        if draft_task_count == 1:
            if text_count > 0 or image_count > 0:
                raise ValueError('draft_task cannot be combined with other content types')
        
        # Validate image roles
        image_items = [item for item in v if item.type == "image_url"]
        if image_items:
            roles = [item.role for item in image_items if item.role is not None]
            
            # Check for conflicting roles
            has_first_frame = "first_frame" in roles
            has_reference_image = "reference_image" in roles
            
            if has_first_frame and has_reference_image:
                raise ValueError('first_frame and reference_image roles cannot be mixed')
            
            # Validate first_frame/last_frame combination
            first_frames = [role for role in roles if role == "first_frame"]
            last_frames = [role for role in roles if role == "last_frame"]
            
            if len(first_frames) > 1:
                raise ValueError('Only one first_frame image is allowed')
            
            if len(last_frames) > 1:
                raise ValueError('Only one last_frame image is allowed')
            
            if len(first_frames) == 0 and len(last_frames) > 0:
                raise ValueError('last_frame requires a corresponding first_frame')
        
        return v

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v):
        if v is not None:
            if v != -1 and (v < 2 or v > 12):
                raise ValueError('Duration must be -1 or between 2 and 12 seconds')
        return v

    @field_validator('frames')
    @classmethod
    def validate_frames(cls, v):
        if v is not None:
            # Check if frame count follows the pattern 25 + 4n where n is positive integer
            if v < 29 or v > 289:
                raise ValueError('Frames must be between 29 and 289')
            
            if (v - 25) % 4 != 0:
                raise ValueError('Frames must follow the pattern 25 + 4n where n is a positive integer')
        
        return v

    @field_validator('resolution', 'ratio', 'duration', 'frames', 'seed', 'camera_fixed', 'watermark')
    @classmethod
    def validate_video_params(cls, v):
        # These are just pass-through validators since Pydantic handles the type validation
        return v

    model_config = ConfigDict(
        # Allow extra fields in case API adds new parameters
        extra="allow",
        # Strict validation
        validate_assignment=True
    )