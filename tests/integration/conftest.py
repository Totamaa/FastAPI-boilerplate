import pytest
from httpx import ASGITransport, AsyncClient

from app.core.api.dependencies.db import get_session
from app.core.security.hash_lib import hash_password
from app.core.security.jwt_lib import create_access_token
from app.modules.users.model import UserModel
from tests.factories import (
    ActorFactory,
    DirectorFactory,
    GenreFactory,
    MovieCastFactory,
    MovieFactory,
    ReviewFactory,
    UserFactory,
)
from tests.helpers.auth import api_key_headers


@pytest.fixture
def _test_app(db_session):
    from app.main import create_app

    app = create_app()

    async def override_session():
        yield db_session

    app.dependency_overrides[get_session] = override_session
    return app


def _async_client(app, headers: dict | None = None):
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers=headers or {},
        follow_redirects=True,
    )


@pytest.fixture
async def client(_test_app):
    """Unauthenticated — public endpoints."""
    async with _async_client(_test_app) as c:
        yield c


@pytest.fixture
async def admin_client(_test_app, settings):
    """API-key authenticated — admin-protected endpoints."""
    async with _async_client(_test_app, api_key_headers(settings.API_KEY)) as c:
        yield c


@pytest.fixture
async def test_user(db_session) -> UserModel:
    """Persisted active non-admin user."""
    user = UserModel(
        email="testuser@example.com",
        hashed_password=hash_password("Testpass1!"),
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def user_client(_test_app, test_user):
    """JWT-authenticated client for test_user."""
    token = create_access_token(test_user.id)
    async with _async_client(_test_app, {"Authorization": f"Bearer {token}"}) as c:
        yield c


@pytest.fixture
async def second_user(db_session) -> UserModel:
    """A second active user — ownership / permission cross-checks."""
    return await UserFactory.create(db_session, email="second@example.com")


@pytest.fixture
async def second_user_client(_test_app, second_user):
    """JWT-authenticated client for second_user."""
    token = create_access_token(second_user.id)
    async with _async_client(_test_app, {"Authorization": f"Bearer {token}"}) as c:
        yield c


# ── Shared resource fixtures ──────────────────────────────────────────────────


@pytest.fixture
async def test_director(db_session):
    return await DirectorFactory.create(db_session)


@pytest.fixture
async def test_actor(db_session):
    return await ActorFactory.create(db_session)


@pytest.fixture
async def test_movie(db_session):
    return await MovieFactory.create(db_session)


@pytest.fixture
async def test_genre(db_session):
    return await GenreFactory.create(db_session)


@pytest.fixture
async def test_review(db_session, test_user, test_movie):
    return await ReviewFactory.create(db_session, user_id=test_user.id, movie_id=test_movie.id)


@pytest.fixture
async def test_cast_entry(db_session, test_movie, test_actor):
    return await MovieCastFactory.create(db_session, movie_id=test_movie.id, actor_id=test_actor.id)
