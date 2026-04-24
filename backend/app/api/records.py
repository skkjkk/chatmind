"""Chat records API routes"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.chat_record import ChatRecord
from app.models.message import Message
from app.schemas.chat_record import (
    ChatRecordResponse,
    ChatRecordDetailResponse,
    ChatRecordListResponse,
    ChatRecordCreate,
    ChatRecordUpdate,
)
from app.core.deps import get_current_user
from app.services.parser import parse_file

router = APIRouter(prefix="/api/records", tags=["Chat Records"])


@router.post("/upload", response_model=ChatRecordResponse, status_code=status.HTTP_201_CREATED)
async def upload_chat_record(
    file: UploadFile = File(...),
    contact_name: str = "",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and parse a chat record file"""
    # Read file content
    content = await file.read()
    content_str = content.decode('utf-8', errors='ignore')

    # Get contact name from filename or parameter
    file_name = file.filename
    if not contact_name:
        contact_name = file_name.replace('.html', '').replace('.txt', '').replace('.json', '')

    # Create record
    record = ChatRecord(
        user_id=current_user.id,
        contact_name=contact_name or "Unknown",
        file_name=file_name,
        file_content=content_str,
        parse_status="parsing"
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    # Parse the file (auto-detect format)
    messages, parse_status = parse_file(file_name, content_str)

    record.parse_status = parse_status

    if parse_status == "success" and messages:
        # Save messages
        for msg in messages:
            message = Message(
                id=str(uuid.uuid4()),
                record_id=record.id,
                sender=msg.sender,
                content=msg.content,
                message_type=msg.message_type,
                timestamp=msg.timestamp,
                is_from_me=msg.is_from_me
            )
            db.add(message)

        record.message_count = len(messages)

    await db.commit()
    await db.refresh(record)

    return record


@router.get("", response_model=ChatRecordListResponse)
async def get_records(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of chat records"""
    result = await db.execute(
        select(ChatRecord)
        .where(ChatRecord.user_id == current_user.id)
        .order_by(ChatRecord.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    records = result.scalars().all()

    # Get total count
    count_result = await db.execute(
        select(ChatRecord).where(ChatRecord.user_id == current_user.id)
    )
    total = len(count_result.scalars().all())

    return ChatRecordListResponse(records=records, total=total)


@router.get("/{record_id}", response_model=ChatRecordDetailResponse)
async def get_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get single record with messages"""
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
        select(Message)
        .where(Message.record_id == record_id)
        .order_by(Message.timestamp)
    )
    messages = msg_result.scalars().all()

    return ChatRecordDetailResponse(
        id=record.id,
        user_id=record.user_id,
        contact_name=record.contact_name,
        file_name=record.file_name,
        message_count=record.message_count,
        parse_status=record.parse_status,
        created_at=record.created_at,
        updated_at=record.updated_at,
        messages=list(messages)
    )


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a chat record"""
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

    await db.delete(record)
    await db.commit()


@router.put("/{record_id}", response_model=ChatRecordResponse)
async def update_record(
    record_id: str,
    data: ChatRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update record (e.g., contact name)"""
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

    if data.contact_name:
        record.contact_name = data.contact_name

    await db.commit()
    await db.refresh(record)

    return record