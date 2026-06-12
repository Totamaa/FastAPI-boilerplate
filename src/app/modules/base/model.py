import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, RelationshipProperty, Session, with_loader_criteria


@event.listens_for(RelationshipProperty, "init")
def _set_default_lazy_raise(target, args, kwargs):
    kwargs.setdefault("lazy", "raise")


class BaseModel(DeclarativeBase):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)


@event.listens_for(Session, "do_orm_execute")
def _apply_soft_delete_filter(execute_state) -> None:
    if (
        execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.is_relationship_load
        and not execute_state.execution_options.get("include_deleted", False)
    ):
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                BaseModel,
                lambda cls: cls.deleted_at.is_(None),
                include_aliases=True,
            )
        )
