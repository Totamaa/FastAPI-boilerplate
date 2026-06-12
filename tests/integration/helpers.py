"""
DB insertion helpers for integration tests.
Prefer using the typed factory classes in tests/factories/ — these helpers
exist for quick one-off insertions that don't need a full factory.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.hash_lib import hash_password
from app.modules.movies.model import MovieModel
from app.modules.users.model import UserModel


async def insert_user(
    db_session: AsyncSession,
    email: str = "helper@example.com",
    password: str = "Testpass1!",
    is_active: bool = True,
) -> UserModel:
    user = UserModel(
        email=email,
        hashed_password=hash_password(password),
        is_active=is_active,
        is_admin=False,
    )
    db_session.add(user)
    await db_session.flush()
    return user


async def insert_movie(
    db_session: AsyncSession,
    title: str = "Test Movie",
    release_year: int = 2024,
) -> MovieModel:
    movie = MovieModel(title=title, release_year=release_year)
    db_session.add(movie)
    await db_session.flush()
    return movie
