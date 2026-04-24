"""Reply suggestion API routes"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.message import Message
from app.models.chat_record import ChatRecord
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


async def _build_context_from_record(record_id: str, user_id: str, db: AsyncSession) -> str:
    """取最近20条消息拼成对话背景"""
    record = (await db.execute(
        select(ChatRecord).where(ChatRecord.id == record_id, ChatRecord.user_id == user_id)
    )).scalar_one_or_none()
    if not record:
        return ""
    msgs = (await db.execute(
        select(Message).where(Message.record_id == record_id)
        .order_by(Message.timestamp.desc()).limit(20)
    )).scalars().all()
    msgs = list(reversed(msgs))
    lines = []
    for m in msgs:
        speaker = "我" if m.is_from_me else record.contact_name
        lines.append(f"{speaker}：{m.content or '[图片/表情]'}")
    return "\n".join(lines)


@router.post("/suggest/stream")
async def stream_smart_suggestion(
    request: SmartContextRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    context = request.context
    if request.record_id:
        context = await _build_context_from_record(request.record_id, current_user.id, db)
    return StreamingResponse(
        reply_engine.stream_smart_reply(request.draft, context, request.style),
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