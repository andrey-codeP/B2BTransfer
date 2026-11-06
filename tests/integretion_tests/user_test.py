import pytest


@pytest.mark.asyncio
async def test_smoke(test_client):
    r = await test_client.get("/docs")
    assert r.status_code == 200
