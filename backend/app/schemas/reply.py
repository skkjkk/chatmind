"""Reply suggestion schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
import json


# Request schemas
class SmartContextRequest(BaseModel):
    """智能语境模式请求"""
    draft: str = Field(..., description="你想回复的话（草稿）")
    context: str = Field("", description="当前对话背景（对方说了什么）")
    style: str = "concise"
    record_id: Optional[str] = Field(None, description="聊天记录ID，自动提取语境")


class QuickQuestionRequest(BaseModel):
    """快速问答模式请求"""
    scenario: str = Field(..., description="场景描述或问题")
    style: str = "concise"


class ImproveDraftRequest(BaseModel):
    """优化草稿请求"""
    draft: str = Field(..., description="需要优化的草稿")
    target_style: str = "concise"


# Response schemas
class ReplySuggestion(BaseModel):
    """单条回复建议"""
    content: str
    style: str
    reason: str


class SmartContextResponse(BaseModel):
    """智能语境模式响应"""
    context_analysis: str
    suggestions: list[ReplySuggestion]
    improved_reply: str


class QuickQuestionResponse(BaseModel):
    """快速问答响应"""
    scenario_analysis: str
    suggestions: list[ReplySuggestion]


class ImproveDraftResponse(BaseModel):
    """优化草稿响应"""
    original: str
    improved: str
    suggestions: list[str]