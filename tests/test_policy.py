from __future__ import annotations

import pytest

from mock import MockPliantClient
from models import Amount


@pytest.mark.asyncio
async def test_get_card_controls_returns_empty_snapshot_by_default() -> None:
    client = MockPliantClient()
    scenario = await client.ensure_scenario(
        scenario_name="Adidas EU Marketing",
        cardholder_name="Anna Schmidt",
        card_currency="EUR",
        card_limit=Amount(value=500000, currency="EUR"),
    )

    controls = await client.get_card_controls(scenario.card_id)

    assert controls.category_controls is None
    assert controls.merchant_controls is None
    assert controls.time_controls == []
    assert controls.amount_controls is None
