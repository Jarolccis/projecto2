import pytest
from unittest.mock import AsyncMock, MagicMock
from app.infrastructure.repositories.user_permissions_repository import UserPermissionsRepository
from app.interfaces.schemas.security_schema import Roles, User
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_get_permissions_by_user_found():
    session = MagicMock()
    repo = UserPermissionsRepository(session)
    result_mock = MagicMock()
    result_mock.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=["PERM1", "PERM2"])))
    session.execute = AsyncMock(return_value=result_mock)
    perms = await repo.get_permissions_by_user([Roles.ACCESS_AGREEMENTS], "user@example.com", 1)
    assert perms == ["PERM1", "PERM2"]

@pytest.mark.asyncio
async def test_get_permissions_by_user_not_found():
    session = MagicMock()
    repo = UserPermissionsRepository(session)
    result_mock = MagicMock()
    result_mock.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
    session.execute = AsyncMock(return_value=result_mock)
    perms = await repo.get_permissions_by_user([Roles.ACCESS_AGREEMENTS], "user@example.com", 1)
    assert perms == []

@pytest.mark.asyncio
async def test_check_db_permissions_success():
    session = MagicMock()
    repo = UserPermissionsRepository(session)
    user = MagicMock(bu_id=1, email="user@example.com")
    repo.get_permissions_by_user = AsyncMock(return_value=[Roles.ACCESS_AGREEMENTS.value])
    result = await repo.check_db_permissions(user, [Roles.ACCESS_AGREEMENTS])
    assert result is True

@pytest.mark.asyncio
async def test_check_db_permissions_missing_bu_id():
    session = MagicMock()
    repo = UserPermissionsRepository(session)
    user = MagicMock(bu_id=None, email="user@example.com")
    with pytest.raises(HTTPException) as excinfo:
        await repo.check_db_permissions(user, [Roles.ACCESS_AGREEMENTS])
    assert excinfo.value.status_code == 400

@pytest.mark.asyncio
async def test_check_db_permissions_missing_email():
    session = MagicMock()
    repo = UserPermissionsRepository(session)
    user = MagicMock(bu_id=1, email=None)
    with pytest.raises(HTTPException) as excinfo:
        await repo.check_db_permissions(user, [Roles.ACCESS_AGREEMENTS])
    assert excinfo.value.status_code == 400

@pytest.mark.asyncio
async def test_check_db_permissions_forbidden():
    session = MagicMock()
    repo = UserPermissionsRepository(session)
    user = MagicMock(bu_id=1, email="user@example.com")
    repo.get_permissions_by_user = AsyncMock(return_value=[])
    with pytest.raises(HTTPException) as excinfo:
        await repo.check_db_permissions(user, [Roles.ACCESS_AGREEMENTS])
    assert excinfo.value.status_code == 403
