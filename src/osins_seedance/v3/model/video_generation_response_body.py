"""Response body model for Volces Video Generation API v3 with strict validation"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class VideoGenerationResponseBody(BaseModel):
    """视频生成任务响应体模型"""

    # Response fields based on API documentation
    id: str = Field(..., description="视频生成任务ID，仅保存7天")
    request_id: Optional[str] = Field(default=None, description="请求ID")
    code: Optional[int] = Field(default=None, description="响应码")
    message: Optional[str] = Field(default=None, description="响应消息")
    created_at: Optional[int] = Field(default=None, description="创建时间戳")
    
    # Task information
    task_info: Optional[Dict[str, Any]] = Field(default=None, description="任务详细信息")
    
    # Error information (if any)
    error: Optional[Dict[str, str]] = Field(default=None, description="错误信息")
    
    # Status information
    status: Optional[str] = Field(default=None, description="任务状态: queued, running, succeeded, failed, expired")
    
    # Video information (when task succeeds)
    video_url: Optional[str] = Field(default=None, description="生成的视频URL")
    video_format: Optional[str] = Field(default=None, description="视频格式")
    duration: Optional[float] = Field(default=None, description="视频时长")
    resolution: Optional[str] = Field(default=None, description="视频分辨率")
    ratio: Optional[str] = Field(default=None, description="视频宽高比")
    
    # Last frame information (if return_last_frame was True)
    last_frame_url: Optional[str] = Field(default=None, description="尾帧图像URL")
    
    # Additional metadata
    model_used: Optional[str] = Field(default=None, description="使用的模型")
    cost: Optional[Dict[str, Any]] = Field(default=None, description="费用信息")
    execution_time: Optional[int] = Field(default=None, description="执行时间")

    model_config = ConfigDict(
        # Allow extra fields in case API returns additional data
        extra="allow",
        # Strict validation
        validate_assignment=True
    )