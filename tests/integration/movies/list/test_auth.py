import pytest

from tests.factories import MovieFactory

pytestmark = pytest.mark.integration
BASE = "/api/v1/movies"


class TestMoviesListAuth:
    async def test_public_endpoint_no_auth(self, client, db_session):
        await MovieFactory.create(db_session)
        assert (await client.get(BASE)).status_code == 200

    async def test_also_works_with_api_key(self, admin_client, db_session):
        await MovieFactory.create(db_session)
        assert (await admin_client.get(BASE)).status_code == 200

    async def test_also_works_authenticated(self, user_client, db_session):
        await MovieFactory.create(db_session)
        assert (await user_client.get(BASE)).status_code == 200
