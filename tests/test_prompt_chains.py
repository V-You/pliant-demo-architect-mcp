from __future__ import annotations

import pytest

from mock import MockPliantClient
from models import Amount, CardControlsInput, CategoryControls, TransactionParams


@pytest.mark.asyncio
async def test_prompt_chain_state_propagates() -> None:
    client = MockPliantClient()
    scenario = await client.ensure_scenario(
        scenario_name="Adidas EU Marketing",
        cardholder_name="Anna Schmidt",
        card_currency="EUR",
        card_limit=Amount(value=500000, currency="EUR"),
    )

    await client.set_card_controls(
        scenario.card_id,
        CardControlsInput(
            category_controls=CategoryControls(
                type="CATEGORY",
                values=["ADVERTISING_AND_MARKETING", "COMPUTING_AND_SOFTWARE"],
                restriction="ALLOWED",
            )
        ),
    )
    transactions = await client.generate_transactions(
        scenario.card_token,
        TransactionParams(count=6, include_blocked=True),
    )
    controls = await client.get_card_controls(scenario.card_id)

    assert controls.category_controls is not None
    assert len(transactions) == 6
    assert scenario.card_token in client.state.transactions
