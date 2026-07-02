"""Comment API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import can_delete_comment, can_edit_comment
from app.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.repository.comments import (
    create_comment,
    delete_comment,
    get_comment_by_id,
    get_photo_comments,
    update_comment,
)
from app.repository.photos import get_photo_by_id
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate

router = APIRouter()


@router.post(
    "/photos/{photo_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_photo_comment(
    photo_id: int,
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CommentResponse:
    photo = await get_photo_by_id(db, photo_id)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )

    comment = await create_comment(
        db,
        photo_id=photo_id,
        user_id=current_user.id,
        text=comment_data.text,
    )
    await db.commit()
    return comment


@router.get("/photos/{photo_id}/comments", response_model=list[CommentResponse])
async def list_photo_comments(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[CommentResponse]:
    photo = await get_photo_by_id(db, photo_id)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found",
        )

    comments = await get_photo_comments(db, photo_id)
    return comments


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_photo_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> CommentResponse:
    comment = await get_comment_by_id(db, comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if not can_edit_comment(comment.user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    comment = await update_comment(db, comment, comment_data.text)
    await db.commit()
    return comment


@router.delete("/comments/{comment_id}")
async def delete_photo_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, str]:
    comment = await get_comment_by_id(db, comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if not can_delete_comment(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    await delete_comment(db, comment)
    await db.commit()
    return {"message": "Comment deleted successfully"}
