from faker import Faker

fake = Faker()

NONEXISTENT_UUID = "00000000-0000-0000-0000-000000000000"
INVALID_UUID = "not-a-valid-uuid"


def user_payload(**overrides) -> dict:
    data = {
        "email": fake.email(),
        "password": "Testpass1!",
        "password_confirm": "Testpass1!",
    }
    data.update(overrides)
    return data


def movie_payload(**overrides) -> dict:
    data = {
        "title": " ".join(fake.words(3)).title(),
        "release_year": fake.random_int(min=1950, max=2024),
    }
    data.update(overrides)
    return data


def actor_payload(**overrides) -> dict:
    data = {"full_name": fake.name()}
    data.update(overrides)
    return data


def director_payload(**overrides) -> dict:
    data = {"full_name": fake.name()}
    data.update(overrides)
    return data


def genre_payload(**overrides) -> dict:
    word = fake.unique.word()
    data = {"name": word.capitalize(), "slug": word.lower()}
    data.update(overrides)
    return data


def review_payload(movie_id, **overrides) -> dict:
    data = {
        "movie_id": str(movie_id),
        "rating": fake.random_int(min=1, max=10),
    }
    data.update(overrides)
    return data


def feature_flag_payload(**overrides) -> dict:
    word = fake.unique.word().lower()
    data = {"key": f"test:{word}", "enabled": True, "rollout_percentage": 100}
    data.update(overrides)
    return data


def cast_payload(movie_id, actor_id, **overrides) -> dict:
    data = {
        "movie_id": str(movie_id),
        "actor_id": str(actor_id),
        "role_name": fake.word().title(),
        "billing_order": fake.random_int(min=1, max=10),
    }
    data.update(overrides)
    return data
