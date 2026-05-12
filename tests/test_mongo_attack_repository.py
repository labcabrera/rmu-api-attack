import pytest

from app.domain.exceptions import AttackNotFoundException
from app.infrastructure.persistence.mongo_attack_repository import MongoAttackRepository


class FakeDatabase:
    attacks = object()


@pytest.mark.asyncio
async def test_find_by_id_with_invalid_object_id_raises_not_found():
    repository = MongoAttackRepository(FakeDatabase())

    with pytest.raises(AttackNotFoundException):
        await repository.find_by_id("not-a-valid-object-id")


@pytest.mark.asyncio
async def test_delete_with_invalid_object_id_returns_false():
    repository = MongoAttackRepository(FakeDatabase())

    assert await repository.delete("not-a-valid-object-id") is False


@pytest.mark.asyncio
async def test_exists_with_invalid_object_id_returns_false():
    repository = MongoAttackRepository(FakeDatabase())

    assert await repository.exists("not-a-valid-object-id") is False
