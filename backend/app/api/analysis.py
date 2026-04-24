"""Analysis API routes"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.chat_record import ChatRecord
from app.models.message import Message
from app.models.analysis import Analysis
from app.schemas.analysis import (
    StatsResponse,
    PersonalityResponse,
    RelationResponse,
    AnalysisStatusResponse,
)
from app.core.deps import get_current_user
from app.services.analyzer import StatsAnalyzer, PersonalityAnalyzer, RelationAnalyzer

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


def _dict_to_camel(obj):
    """Convert snake_case dict keys to camelCase for response"""
    if isinstance(obj, dict):
        return {to_camel(k): v for k, v in obj.items()}
    return obj


def to_camel(snake_str):
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


@router.post("/{record_id}", status_code=status.HTTP_202_ACCEPTED)
async def run_analysis(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Run full analysis on a chat record"""
    # Get record
    result = await db.execute(
        select(ChatRecord).where(
            ChatRecord.id == record_id,
            ChatRecord.user_id == current_user.id
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found"
        )

    # Get messages
    msg_result = await db.execute(
        select(Message).where(Message.record_id == record_id)
    )
    messages = list(msg_result.scalars().all())

    if not messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages to analyze"
        )

    # Run analyses
    stats = StatsAnalyzer.analyze(messages)
    personality = PersonalityAnalyzer.analyze(messages)
    relation = RelationAnalyzer.analyze(messages)

    # Save results
    analyses_data = [
        ("stats", stats),
        ("personality", personality),
        ("relation", relation),
    ]

    for atype, data in analyses_data:
        # Delete old analysis if exists
        old = await db.execute(
            select(Analysis).where(
                Analysis.record_id == record_id,
                Analysis.analysis_type == atype
            )
        )
        old_result = old.scalar_one_or_none()
        if old_result:
            await db.delete(old_result)

        # Create new analysis
        analysis = Analysis(
            record_id=record_id,
            analysis_type=atype,
            result_data=json.dumps(data, ensure_ascii=False)
        )
        db.add(analysis)

    await db.commit()

    return {"message": "Analysis completed", "record_id": record_id}


@router.get("/{record_id}/stats", response_model=StatsResponse)
async def get_stats(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics analysis"""
    # Check record ownership
    result = await db.execute(
        select(ChatRecord).where(
            ChatRecord.id == record_id,
            ChatRecord.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Record not found")

    # Get or compute stats
    stats = await _get_or_compute_analysis(db, record_id, "stats")
    return stats


@router.get("/{record_id}/personality", response_model=PersonalityResponse)
async def get_personality(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get personality analysis"""
    result = await db.execute(
        select(ChatRecord).where(
            ChatRecord.id == record_id,
            ChatRecord.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Record not found")

    personality = await _get_or_compute_analysis(db, record_id, "personality")
    return personality


@router.get("/{record_id}/relation", response_model=RelationResponse)
async def get_relation(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get relationship analysis"""
    result = await db.execute(
        select(ChatRecord).where(
            ChatRecord.id == record_id,
            ChatRecord.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Record not found")

    relation = await _get_or_compute_analysis(db, record_id, "relation")
    return relation


async def _get_or_compute_analysis(db: AsyncSession, record_id: str, analysis_type: str) -> dict:
    """Get analysis from DB or compute if not exists"""
    result = await db.execute(
        select(Analysis).where(
            Analysis.record_id == record_id,
            Analysis.analysis_type == analysis_type
        )
    )
    analysis = result.scalar_one_or_none()

    if analysis:
        return json.loads(analysis.result_data)

    # Compute if not exists
    msg_result = await db.execute(
        select(Message).where(Message.record_id == record_id)
    )
    messages = list(msg_result.scalars().all())

    if analysis_type == "stats":
        return StatsAnalyzer.analyze(messages)
    elif analysis_type == "personality":
        return PersonalityAnalyzer.analyze(messages)
    elif analysis_type == "relation":
        return RelationAnalyzer.analyze(messages)

    return {}