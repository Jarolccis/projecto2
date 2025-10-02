import pytest

class HealthyUseCase:
    async def check(self):
        return {"status": "healthy"}

@pytest.mark.asyncio
async def test_healthy_usecase():
    usecase = HealthyUseCase()
    result = await usecase.check()
    assert result == {"status": "healthy"}
