import pytest

from app.db.database import User
from app.dependencies import get_user_repo, get_user_service
from app.errors.exceptions import BusinessRuleError
from app.schemas import UserRegister

DUMMY_SECURE_HASH = "$2b$12$e86gOzU4mO8hE7gYQx3x8.0yY2B5V3d3gS4v2X6M0F2k6P1q9e7W2"


@pytest.fixture
def user_service(db_session):
    repo = get_user_repo(db_session)
    service = get_user_service(repo)
    return service


@pytest.fixture
async def seed_user(db_session) -> User:
    user = User(
        email="user_a@hesabi.com",
        password_hash=DUMMY_SECURE_HASH,
        name="User A",
        is_active=True,
    )

    db_session.add(user)
    await db_session.flush()
    return user


class TestUserService:
    async def test_user_register_success(self, user_service):
        payload = UserRegister(
            email="new_user@hesabi.com",
            password="StrongPassword123!",
            name="New User",
        )
        response = await user_service.user_register(payload)

        assert response.id is not None
        assert response.email == "new_user@hesabi.com"
        assert response.is_active is True

    async def test_user_register_user_exist(self, user_service, seed_user):
        payload = UserRegister(
            email=seed_user.email,
            password="StrongPassword123!",
            name=seed_user.name,
        )
        with pytest.raises(BusinessRuleError) as exc_info:
            await user_service.user_register(payload)

        assert exc_info.value.error_code == "EMAIL_ALREADY_EXISTS"
