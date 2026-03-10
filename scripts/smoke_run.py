from __future__ import annotations

import asyncio
import json
from typing import Any

import server


def unpack_result(result: Any) -> Any:
    structured = getattr(result, "structured_content", None)
    if structured not in (None, {}):
        return structured

    content = getattr(result, "content", None) or []
    for item in content:
        item_type = getattr(item, "type", None)
        if item_type == "text":
            text = getattr(item, "text", "")
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text

    return result


def assert_ok(payload: Any, step: str) -> None:
    if isinstance(payload, dict) and payload.get("status") == "error":
        raise RuntimeError(f"{step} failed: {payload}")


async def main() -> None:
    scenario = unpack_result(
        await server.mcp.call_tool(
            "setup_demo_scenario",
            {
                "scenario_name": "Adidas EU Marketing",
                "cardholder_name": "Anna Schmidt",
                "card_currency": "EUR",
                "card_limit": {"value": 500000, "currency": "EUR"},
            },
        )
    )
    assert_ok(scenario, "setup_demo_scenario")

    card_token = scenario["card_token"]
    card_account_id = scenario["card_account_id"]

    controls = unpack_result(
        await server.mcp.call_tool(
            "set_card_controls",
            {
                "card_token": card_token,
                "allowed_categories": [
                    "ADVERTISING_AND_MARKETING",
                    "COMPUTING_AND_SOFTWARE",
                ],
                "time_windows": [
                    {
                        "days": [
                            "MONDAY",
                            "TUESDAY",
                            "WEDNESDAY",
                            "THURSDAY",
                            "FRIDAY",
                        ],
                        "start_time": "08:00",
                        "end_time": "18:00",
                        "timezone": "Europe/Berlin",
                    }
                ],
                "per_transaction_limit": {"value": 200000, "currency": "EUR"},
            },
        )
    )
    assert_ok(controls, "set_card_controls")

    transactions = unpack_result(
        await server.mcp.call_tool(
            "generate_demo_data",
            {
                "card_token": card_token,
                "count": 8,
                "include_blocked": True,
            },
        )
    )
    assert_ok(transactions, "generate_demo_data")

    policy = unpack_result(
        await server.mcp.call_tool(
            "test_spend_policy",
            {
                "card_token": card_token,
                "scenario": "Can Anna buy a EUR 300 Google Ads subscription on Monday at 10am?",
            },
        )
    )
    assert_ok(policy, "test_spend_policy")

    callbacks = unpack_result(
        await server.mcp.call_tool(
            "diagnose_callbacks",
            {
                "card_account_id": card_account_id,
                "status_filter": "FAILED",
                "limit": 5,
            },
        )
    )
    assert_ok(callbacks, "diagnose_callbacks")

    print("smoke run complete")
    print(f"scenario: {scenario['scenario_name']}")
    print(f"card token: {card_token}")
    print(f"transactions created: {transactions['transactions_created']}")
    print(f"controls summary: {policy['controls_summary']}")
    print(f"callback failures returned: {len(callbacks['events'])}")


if __name__ == "__main__":
    asyncio.run(main())