from __future__ import annotations

import pytest

from mock import MockPliantClient
from models import Amount


@pytest.mark.asyncio
async def test_setup_demo_scenario_is_idempotent() -> None:
    client = MockPliantClient()

    first = await client.ensure_scenario(
        scenario_name="Adidas EU Marketing",
        cardholder_name="Anna Schmidt",
        card_currency="EUR",
        card_limit=Amount(value=500000, currency="EUR"),
    )
    second = await client.ensure_scenario(
        scenario_name="Adidas EU Marketing",
        cardholder_name="Anna Schmidt",
        card_currency="EUR",
        card_limit=Amount(value=500000, currency="EUR"),
    )

    assert first == second
    assert first.card_token in client.state.cards
    assert first.scenario_name in client.state.scenarios
