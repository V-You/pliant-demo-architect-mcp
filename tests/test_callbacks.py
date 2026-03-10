from __future__ import annotations

import pytest

from mock import MockPliantClient
from models import Amount


@pytest.mark.asyncio
async def test_callback_health_is_seeded_and_counted() -> None:
    client = MockPliantClient()
    scenario = await client.ensure_scenario(
        scenario_name="Adidas EU Marketing",
        cardholder_name="Anna Schmidt",
        card_currency="EUR",
        card_limit=Amount(value=500000, currency="EUR"),
    )

    callback_log = await client.get_callback_log(scenario.card_account_id)

    assert callback_log.total_events == 47
    assert callback_log.success_count == 42
    assert callback_log.failure_count == 5
    assert callback_log.circuit_breaker in {"OPEN", "CLOSED"}
