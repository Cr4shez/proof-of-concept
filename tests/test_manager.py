from io import BytesIO

import pytest


@pytest.mark.parametrize("content", [
    b"This is a test",
    b"This is a test that will rule the universe\n\r" * 10
])
async def test_manager_success(manager, content):
    await manager.backup(BytesIO(content))

    out = BytesIO()
    await manager.restore(out)
    assert out.read() == content

