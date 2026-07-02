from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.dependencies import get_current_active_user, require_roles
from app.models.user import User, UserRole


require_admin = require_roles(UserRole.ADMIN)

require_moderator_or_admin = require_roles(UserRole.MODERATOR, UserRole.ADMIN)


def can_modify_photo(photo_user_id: int, current_user: User) -> bool:
    return current_user.role == UserRole.ADMIN or current_user.id == photo_user_id


def can_edit_comment(comment_user_id: int, current_user: User) -> bool:
    return current_user.id == comment_user_id


def can_delete_comment(current_user: User) -> bool:
    return current_user.role in {UserRole.MODERATOR, UserRole.ADMIN}


def require_owner_or_admin(owner_id: int) -> Callable:
    async def _require_owner_or_admin(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role != UserRole.ADMIN and current_user.id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _require_owner_or_admin
