import pytest

from app.crud.user import UserCRUD
from app.schemas.user import UserCreate, UserUpdate

from app.tests.test_pg_db import test_session


@pytest.mark.asyncio
async def test_user_crud():
    user_crud = UserCRUD(test_session)

    users = await user_crud.get_all_users(limit=10, offset=0)
    assert users["total"] >= 0

    user = await user_crud.get_user_by_id(user_id=44)
    assert user is None

    user_create = UserCreate(
        username="botttt", email="botttt@example.com", password="bottttpwdkakdawdnanjc"
    )
    new_user = await user_crud.create_new_user(user_create)
    assert new_user.username == "botttt"
    assert new_user.email == "botttt@example.com"

    user_update = UserUpdate(
        username="updatedbot", email="updatedbot@example.com", password="newpassword"
    )
    updated_user = await user_crud.update_user_by_id(new_user.id, user_update)
    assert updated_user.username == "updatedbot"
    assert updated_user.email == "updatedbot@example.com"

    deleted_user = await user_crud.delete_user_by_id(new_user.id)
    assert deleted_user.id == new_user.id
    assert await user_crud.get_user_by_id(new_user.id) is None
