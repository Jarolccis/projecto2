import pytest

class HealthyRepository:
    async def get_status(self):
        return {"status": "healthy"}

@pytest.mark.asyncio
async def test_healthy_repository():
    repo = HealthyRepository()
    result = await repo.get_status()
    assert result == {"status": "healthy"}
