from __future__ import annotations

import pytest

import server
from mock import MockPliantClient


@pytest.fixture
def isolated_server_client(monkeypatch: pytest.MonkeyPatch) -> MockPliantClient:
    client = MockPliantClient()
    monkeypatch.setattr(server, "client", client)
    return client
