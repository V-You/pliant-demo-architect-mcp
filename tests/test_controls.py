from __future__ import annotations

import pytest

from mock import MockPliantClient
from models import Amount, CardControlsInput, CategoryControls


@pytest.mark.asyncio
async def test_set_and_get_card_controls() -> None:
    client = MockPliantClient()
    scenario = await client.ensure_scenario(
        scenario_name="Adidas EU Marketing",
        cardholder_name="Anna Schmidt",
        card_currency="EUR",
        card_limit=Amount(value=500000, currency="EUR"),
    )

    controls = await client.set_card_controls(
        scenario.card_id,
        CardControlsInput(
            category_controls=CategoryControls(
                type="CATEGORY",
                values=["ADVERTISING_AND_MARKETING", "COMPUTING_AND_SOFTWARE"],
                restriction="ALLOWED",
            )
        ),
    )

    fetched = await client.get_card_controls(scenario.card_id)

    assert controls == fetched
    assert fetched.category_controls is not None
    assert fetched.category_controls.restriction == "ALLOWED"
