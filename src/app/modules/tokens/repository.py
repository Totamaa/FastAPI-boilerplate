import hashlib
import secrets
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tokens.model import RefreshTokenFamilyModel, RefreshTokenModel


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


class TokenRepository:
    async def create_family(
        self,
        user_id: UUID,
        user_agent: str | None,
        ip_address: str | None,
        db: AsyncSession,
    ) -> RefreshTokenFamilyModel:
        family = RefreshTokenFamilyModel(
            user_id=user_id,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        db.add(family)
        await db.flush()
        return family

    async def create_token(
        self,
        family_id: UUID,
        parent_id: UUID | None,
        expires_at: datetime,
        db: AsyncSession,
    ) -> tuple[str, RefreshTokenModel]:
        raw = secrets.token_urlsafe(32)
        token = RefreshTokenModel(
            token_hash=_hash_token(raw),
            family_id=family_id,
            parent_id=parent_id,
            expires_at=expires_at,
        )
        db.add(token)
        await db.flush()
        return raw, token

    async def get_token_by_raw(
        self,
        raw: str,
        db: AsyncSession,
    ) -> RefreshTokenModel | None:
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token_hash == _hash_token(raw))
        result = await db.execute(stmt)
        return result.scalars().one_or_none()

    async def get_family(
        self,
        family_id: UUID,
        db: AsyncSession,
        include_revoked: bool = False,
    ) -> RefreshTokenFamilyModel | None:
        stmt = select(RefreshTokenFamilyModel).where(RefreshTokenFamilyModel.id == family_id)
        if include_revoked:
            stmt = stmt.execution_options(include_deleted=True)
        result = await db.execute(stmt)
        return result.scalars().one_or_none()

    async def mark_token_used(self, token: RefreshTokenModel, db: AsyncSession) -> None:
        token.used_at = datetime.now(UTC)
        await db.flush()

    async def revoke_family(self, family_id: UUID, db: AsyncSession) -> None:
        stmt = (
            update(RefreshTokenFamilyModel)
            .where(RefreshTokenFamilyModel.id == family_id)
            .values(deleted_at=datetime.now(UTC))
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(stmt)
        await db.flush()

    async def revoke_all_user_families(self, user_id: UUID, db: AsyncSession) -> None:
        now = datetime.now(UTC)
        stmt = (
            update(RefreshTokenFamilyModel)
            .where(
                RefreshTokenFamilyModel.user_id == user_id,
                RefreshTokenFamilyModel.deleted_at.is_(None),
            )
            .values(deleted_at=now)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(stmt)
        await db.flush()

    async def get_active_families(
        self,
        user_id: UUID,
        db: AsyncSession,
    ) -> list[RefreshTokenFamilyModel]:
        stmt = select(RefreshTokenFamilyModel).where(RefreshTokenFamilyModel.user_id == user_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def delete_expired_tokens(self, db: AsyncSession) -> int:
        from sqlalchemy import delete

        now = datetime.now(UTC)
        result = await db.execute(
            delete(RefreshTokenModel).where(RefreshTokenModel.expires_at < now)
        )
        return result.rowcount
