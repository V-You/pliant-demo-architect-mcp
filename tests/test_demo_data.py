from __future__ import annotations

import pytest

from mock import MockPliantClient
from models import Amount, CategoryControls, CardControlsInput, TransactionParams


@pytest.mark.asyncio
async def test_generate_demo_data_can_include_declined_transactions() -> None:
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
                values=["ADVERTISING_AND_MARKETING"],
                restriction="ALLOWED",
            )
        ),
    )

    transactions = await client.generate_transactions(
        scenario.card_token,
        TransactionParams(count=8, include_blocked=True),
    )

    assert len(transactions) == 8
    assert any(transaction.status == "DECLINED" for transaction in transactions)
