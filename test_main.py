import pytest

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.mark.parametrize("path, route_index", [
    ("/v1/webhook/invoice", 4),
])
def test_main_routes(path: str, route_index: int):
    assert path == client.app.routes[route_index].path
