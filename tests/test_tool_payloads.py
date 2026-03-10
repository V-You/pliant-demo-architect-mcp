from __future__ import annotations

import pytest

import server
from helpers import unpack_tool_result


@pytest.mark.asyncio
async def test_setup_demo_scenario_payload_shape(isolated_server_client) -> None:
    result = await server.mcp.call_tool(
        "setup_demo_scenario",
        {
            "scenario_name": "Adidas EU Marketing",
            "cardholder_name": "Anna Schmidt",
            "card_currency": "EUR",
            "card_limit": {"value": 500000, "currency": "EUR"},
        },
    )
    payload = unpack_tool_result(result)

    assert set(payload) == {
        "scenario_name",
        "org_id",
        "card_account_id",
        "cardholder_id",
        "card_token",
        "card_id",
        "card_currency",
        "card_limit",
        "status",
        "message",
    }
    assert payload["scenario_name"] == "Adidas EU Marketing"
    assert payload["card_currency"] == "EUR"
    assert payload["card_limit"] == {"value": 500000, "currency": "EUR"}
    assert payload["status"] == "ready"
    assert "Sandbox scenario 'Adidas EU Marketing' is ready." in payload["message"]


@pytest.mark.asyncio
async def test_set_card_controls_payload_shape(isolated_server_client) -> None:
    scenario = unpack_tool_result(
        await server.mcp.call_tool(
            "setup_demo_scenario",
            {
                "scenario_name": "Adidas EU Marketing",
                "cardholder_name": "Anna Schmidt",
            },
        )
    )

    result = await server.mcp.call_tool(
        "set_card_controls",
        {
            "card_token": scenario["card_token"],
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
    payload = unpack_tool_result(result)

    assert set(payload) == {"card_token", "controls_applied", "controls", "message"}
    assert payload["card_token"] == scenario["card_token"]
    assert payload["controls_applied"] is True
    assert payload["message"] == "Card controls updated."
    assert payload["controls"]["category_controls"] == {
        "type": "CATEGORY",
        "values": ["ADVERTISING_AND_MARKETING", "COMPUTING_AND_SOFTWARE"],
        "restriction": "ALLOWED",
    }
    assert payload["controls"]["merchant_controls"] is None
    assert payload["controls"]["amount_controls"] == {
        "per_transaction": {"value": 200000, "currency": "EUR"},
        "periodic": None,
    }


@pytest.mark.asyncio
async def test_set_card_controls_error_envelope(isolated_server_client) -> None:
    scenario = unpack_tool_result(
        await server.mcp.call_tool(
            "setup_demo_scenario",
            {
                "scenario_name": "Conflict Demo",
                "cardholder_name": "Alex Example",
            },
        )
    )

    result = await server.mcp.call_tool(
        "set_card_controls",
        {
            "card_token": scenario["card_token"],
            "allowed_categories": ["ADVERTISING_AND_MARKETING"],
            "blocked_categories": ["OTHER"],
        },
    )
    payload = unpack_tool_result(result)

    assert payload == {
        "status": "error",
        "failed_step": "set_card_controls",
        "error": "Provide either allowed_categories or blocked_categories, not both.",
    }


@pytest.mark.asyncio
async def test_test_spend_policy_payload_shape(isolated_server_client) -> None:
    scenario = unpack_tool_result(
        await server.mcp.call_tool(
            "setup_demo_scenario",
            {
                "scenario_name": "Adidas EU Marketing",
                "cardholder_name": "Anna Schmidt",
            },
        )
    )
    await server.mcp.call_tool(
        "set_card_controls",
        {
            "card_token": scenario["card_token"],
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

    result = await server.mcp.call_tool(
        "test_spend_policy",
        {
            "card_token": scenario["card_token"],
            "scenario": "Can Anna buy a EUR 300 Google Ads subscription on Monday at 10am?",
        },
    )
    payload = unpack_tool_result(result)

    assert set(payload) == {
        "card_token",
        "card_last_four",
        "cardholder",
        "card_currency",
        "card_limit",
        "scenario",
        "controls",
        "category_labels",
        "merchant_category_map",
        "controls_summary",
        "instruction",
    }
    assert payload["cardholder"] == {"name": "Anna Schmidt", "team": "EU Marketing"}
    assert payload["card_currency"] == "EUR"
    assert payload["controls"]["category_controls"]["restriction"] == "ALLOWED"
    assert payload["category_labels"]["ADVERTISING_AND_MARKETING"] == "Advertising & Marketing"
    assert "Google Ads" in payload["merchant_category_map"]["ADVERTISING_AND_MARKETING"]
    assert payload["controls_summary"].startswith("Allowed: ADVERTISING_AND_MARKETING")
    assert payload["instruction"].startswith("Evaluate the scenario against the controls above.")


@pytest.mark.asyncio
async def test_generate_demo_data_payload_shape(isolated_server_client) -> None:
    scenario = unpack_tool_result(
        await server.mcp.call_tool(
            "setup_demo_scenario",
            {
                "scenario_name": "Adidas EU Marketing",
                "cardholder_name": "Anna Schmidt",
            },
        )
    )

    result = await server.mcp.call_tool(
        "generate_demo_data",
        {
            "card_token": scenario["card_token"],
            "count": 8,
            "include_blocked": True,
        },
    )
    payload = unpack_tool_result(result)

    assert set(payload) == {
        "card_token",
        "transactions_created",
        "summary",
        "transactions",
        "note",
    }
    assert payload["card_token"] == scenario["card_token"]
    assert payload["transactions_created"] == 8
    assert set(payload["summary"]) == {
        "total_amount",
        "categories",
        "statuses",
        "date_range",
    }
    assert len(payload["transactions"]) == 8
    assert payload["summary"]["statuses"]["DECLINED"] >= 1
    assert payload["note"].startswith("Sandbox transactions appear as PENDING")


@pytest.mark.asyncio
async def test_diagnose_callbacks_payload_shape(isolated_server_client) -> None:
    scenario = unpack_tool_result(
        await server.mcp.call_tool(
            "setup_demo_scenario",
            {
                "scenario_name": "Adidas EU Marketing",
                "cardholder_name": "Anna Schmidt",
            },
        )
    )

    result = await server.mcp.call_tool(
        "diagnose_callbacks",
        {
            "card_account_id": scenario["card_account_id"],
            "status_filter": "FAILED",
            "limit": 5,
        },
    )
    payload = unpack_tool_result(result)

    assert set(payload) == {
        "card_account_id",
        "callback_health",
        "subscriptions",
        "events",
        "retry_strategy",
        "security_note",
    }
    assert payload["callback_health"] == {
        "total_events": 47,
        "success_count": 42,
        "failure_count": 5,
        "success_rate": "89.4%",
        "circuit_breaker": "CLOSED",
    }
    assert len(payload["subscriptions"]) == 1
    assert len(payload["events"]) == 5
    assert all(event["status"] == "FAILED" for event in payload["events"])
    assert payload["retry_strategy"]["4xx_errors"].startswith("~5 retries")
    assert payload["security_note"].startswith("Callbacks are signed using Ed25519")


@pytest.mark.asyncio
async def test_tool_level_prompt_chain_state_propagates(isolated_server_client) -> None:
    scenario = unpack_tool_result(
        await server.mcp.call_tool(
            "setup_demo_scenario",
            {
                "scenario_name": "Adidas EU Marketing",
                "cardholder_name": "Anna Schmidt",
            },
        )
    )
    controls = unpack_tool_result(
        await server.mcp.call_tool(
            "set_card_controls",
            {
                "card_token": scenario["card_token"],
                "allowed_categories": [
                    "ADVERTISING_AND_MARKETING",
                    "COMPUTING_AND_SOFTWARE",
                ],
            },
        )
    )
    transactions = unpack_tool_result(
        await server.mcp.call_tool(
            "generate_demo_data",
            {
                "card_token": scenario["card_token"],
                "count": 6,
                "include_blocked": True,
            },
        )
    )
    policy = unpack_tool_result(
        await server.mcp.call_tool(
            "test_spend_policy",
            {
                "card_token": scenario["card_token"],
                "scenario": "Can Anna buy Google Ads?",
            },
        )
    )

    assert controls["controls"]["category_controls"]["values"] == [
        "ADVERTISING_AND_MARKETING",
        "COMPUTING_AND_SOFTWARE",
    ]
    assert transactions["transactions_created"] == 6
    assert policy["controls"]["category_controls"]["values"] == [
        "ADVERTISING_AND_MARKETING",
        "COMPUTING_AND_SOFTWARE",
    ]
    assert policy["card_token"] == scenario["card_token"]
