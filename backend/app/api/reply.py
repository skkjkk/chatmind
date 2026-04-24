"""Reply suggestion API routes"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.models.user import User
from app.schemas.reply import (
    SmartContextRequest,
    SmartContextResponse,
    QuickQuestionRequest,
    QuickQuestionResponse,
    ImproveDraftRequest,
    ImproveDraftResponse,
)
from app.core.deps import get_current_user
from app.services.reply_engine import ReplyEngine

router = APIRouter(prefix="/api/reply", tags=["Reply"])

reply_engine = ReplyEngine()


@router.post("/suggest/stream")
async def stream_smart_suggestion(
    request: SmartContextRequest,
    current_user: User = Depends(get_current_user)
):
    return StreamingResponse(
        reply_engine.stream_smart_reply(request.draft, request.context, request.style),
        media_type="text/event-stream"
    )


@router.post("/quick/stream")
async def stream_quick_suggestion(
    request: QuickQuestionRequest,
    current_user: User = Depends(get_current_user)
):
    return StreamingResponse(
        reply_engine.stream_quick_reply(request.scenario, request.style),
        media_type="text/event-stream"
    )


@router.post("/suggest", response_model=SmartContextResponse)
async def get_smart_context_suggestion(
    request: SmartContextRequest,
    current_user: User = Depends(get_current_user)
):
    """智能语境模式 - 基于对话背景优化回复"""
    result = await reply_engine.smart_context_reply(
        draft=request.draft,
        context=request.context,
        style=request.style
    )
    return result


@router.post("/quick", response_model=QuickQuestionResponse)
async def get_quick_question_suggestion(
    request: QuickQuestionRequest,
    current_user: User = Depends(get_current_user)
):
    """快速问答模式 - 直接给出回复建议"""
    result = await reply_engine.quick_question_reply(
        scenario=request.scenario,
        style=request.style
    )
    return result


@router.post("/improve", response_model=ImproveDraftResponse)
async def improve_draft(
    request: ImproveDraftRequest,
    current_user: User = Depends(get_current_user)
):
    """优化用户草稿"""
    result = await reply_engine.improve_draft(
        draft=request.draft,
        target_style=request.target_style
    )

    # Ensure keys match schema
    return ImproveDraftResponse(
        original=result.get("original", request.draft),
        improved=result.get("improved", request.draft),
        suggestions=result.get("suggestions", [])
    )