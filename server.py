from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.apps import AppConfig, ResourceCSP
from fastmcp.tools import ToolResult

from apps import CALLBACK_DASHBOARD_URI, CONTROLS_CARD_URI
from apps.callback_dashboard import render_callback_dashboard_html
from apps.controls_card import render_controls_card_html
from fixtures import (
    CATEGORY_LABELS,
    DEFAULT_CALLBACK_RETRY_STRATEGY,
    DEFAULT_CALLBACK_SECURITY_NOTE,
    merchant_names_by_category,
)
from mock import MockPliantClient
from models import (
    Amount,
    AmountControls,
    AmountRange,
    CardControlsInput,
    CategoryControls,
    MerchantControls,
    PeriodicLimit,
    TimeControl,
    TransactionParams,
)

load_dotenv()

mcp = FastMCP("Pliant Demo Architect MCP")
client = MockPliantClient()


def _tool_error(failed_step: str, error: Exception | str) -> dict[str, str]:
    return {
        "status": "error",
        "failed_step": failed_step,
        "error": str(error),
    }


def _json_result(payload: dict[str, Any]) -> ToolResult:
    return ToolResult(content=json.dumps(payload, default=str))


def _format_amount(amount: Amount | None) -> str:
    if amount is None:
        return "none"
    return f"{amount.currency} {amount.value / 100:,.2f}"


def _controls_summary(controls: dict[str, Any]) -> str:
    if not any(
        [
            controls.get("category_controls"),
            controls.get("merchant_controls"),
            controls.get("time_controls"),
            controls.get("amount_controls"),
        ]
    ):
        return "No restrictions active."

    parts: list[str] = []
    category_controls = controls.get("category_controls")
    if category_controls:
        parts.append(
            f"{category_controls['restriction'].title()}: {', '.join(category_controls['values'])}"
        )

    time_controls = controls.get("time_controls") or []
    if time_controls:
        first_window = time_controls[0]
        parts.append(
            f"{', '.join(first_window['days'])} {first_window['start_time']}-{first_window['end_time']} {first_window['timezone']}"
        )

    amount_controls = controls.get("amount_controls") or {}
    per_transaction = amount_controls.get("per_transaction")
    if per_transaction:
        parts.append(
            f"Max {_format_amount(Amount.model_validate(per_transaction))} per transaction"
        )

    return ". ".join(parts) + "."


def _build_amount_controls(
    per_transaction_limit: dict[str, Any] | None,
    periodic_limit: dict[str, Any] | None,
) -> AmountControls | None:
    if per_transaction_limit is None and periodic_limit is None:
        return None

    periodic = None
    if periodic_limit is not None:
        periodic = PeriodicLimit(
            amount=Amount.model_validate(periodic_limit["amount"]),
            period=periodic_limit["period"],
        )

    return AmountControls(
        per_transaction=(
            Amount.model_validate(per_transaction_limit)
            if per_transaction_limit is not None
            else None
        ),
        periodic=periodic,
    )


@mcp.tool
async def setup_demo_scenario(
    scenario_name: str,
    cardholder_name: str,
    card_currency: str = "EUR",
    card_limit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create or return a deterministic mock demo scenario."""
    try:
        limit = None
        if card_limit is not None:
            limit = Amount.model_validate(card_limit)
        else:
            limit = Amount(value=500000, currency=card_currency)

        scenario = await client.ensure_scenario(
            scenario_name,
            cardholder_name,
            card_currency,
            limit,
        )
        card = client.get_card_by_token(scenario.card_token)
        cardholder = client.state.cardholders[scenario.cardholder_id]

        return {
            "scenario_name": scenario.scenario_name,
            "org_id": scenario.org_id,
            "card_account_id": scenario.card_account_id,
            "cardholder_id": scenario.cardholder_id,
            "card_token": scenario.card_token,
            "card_id": scenario.card_id,
            "card_currency": card.currency,
            "card_limit": card.limit.model_dump() if card.limit else None,
            "status": "ready",
            "message": (
                f"Sandbox scenario '{scenario_name}' is ready. "
                f"Card issued to {cardholder.first_name} {cardholder.last_name} "
                f"with {_format_amount(card.limit)} limit."
            ),
        }
    except Exception as exc:  # pragma: no cover - defensive tool boundary
        return _tool_error("setup_demo_scenario", exc)


@mcp.tool
async def set_card_controls(
    card_token: str,
    allowed_categories: list[str] | None = None,
    blocked_categories: list[str] | None = None,
    merchant_controls: dict[str, Any] | None = None,
    time_windows: list[dict[str, Any]] | None = None,
    per_transaction_limit: dict[str, Any] | None = None,
    periodic_limit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Configure mock card controls for a card."""
    try:
        if allowed_categories and blocked_categories:
            return _tool_error(
                "set_card_controls",
                "Provide either allowed_categories or blocked_categories, not both.",
            )

        card = client.get_card_by_token(card_token)
        category_controls = None
        if allowed_categories:
            category_controls = CategoryControls(
                type="CATEGORY",
                values=allowed_categories,
                restriction="ALLOWED",
            )
        elif blocked_categories:
            category_controls = CategoryControls(
                type="CATEGORY",
                values=blocked_categories,
                restriction="BLOCKED",
            )

        controls_input = CardControlsInput(
            category_controls=category_controls,
            merchant_controls=(
                MerchantControls.model_validate(merchant_controls)
                if merchant_controls is not None
                else None
            ),
            time_controls=[
                TimeControl.model_validate(window) for window in (time_windows or [])
            ],
            amount_controls=_build_amount_controls(
                per_transaction_limit,
                periodic_limit,
            ),
        )
        controls = await client.set_card_controls(card.card_id, controls_input)
        payload = controls.model_dump()
        return {
            "card_token": card_token,
            "controls_applied": True,
            "controls": payload,
            "message": "Card controls updated.",
        }
    except Exception as exc:  # pragma: no cover - defensive tool boundary
        return _tool_error("set_card_controls", exc)


@mcp.tool(app=AppConfig(resource_uri=CONTROLS_CARD_URI))
async def test_spend_policy(
    card_token: str,
    scenario: str | None = None,
) -> ToolResult:
    """Return structured card controls data for LLM reasoning and UI rendering."""
    try:
        card = client.get_card_by_token(card_token)
        controls = await client.get_card_controls(card.card_id)
        cardholder = client.state.cardholders[card.cardholder_id]
        controls_payload = controls.model_dump()
        payload = {
            "card_token": card.token,
            "cardholder": {
                "name": f"{cardholder.first_name} {cardholder.last_name}".strip(),
                "team": cardholder.team,
            },
            "card_currency": card.currency,
            "card_limit": card.limit.model_dump() if card.limit else None,
            "scenario": scenario,
            "controls": controls_payload,
            "merchant_category_map": merchant_names_by_category(),
            "controls_summary": _controls_summary(controls_payload),
            "instruction": (
                "Evaluate the scenario against the controls above. State ALLOWED "
                "or BLOCKED, and cite the specific control rule that determines "
                "the outcome."
            ),
        }
        return _json_result(payload)
    except Exception as exc:  # pragma: no cover - defensive tool boundary
        return _json_result(_tool_error("test_spend_policy", exc))


@mcp.tool
async def generate_demo_data(
    card_token: str,
    count: int = 5,
    category: str | None = None,
    amount_range: dict[str, Any] | None = None,
    merchant_name: str | None = None,
    status: str = "CONFIRMED",
    include_blocked: bool = False,
) -> dict[str, Any]:
    """Generate deterministic mock transactions for a card."""
    try:
        params = TransactionParams(
            count=count,
            category=category,
            amount_range=(
                AmountRange.model_validate(amount_range) if amount_range else None
            ),
            merchant_name=merchant_name,
            status=status,
            include_blocked=include_blocked,
        )
        transactions = await client.generate_transactions(card_token, params)
        amounts = [transaction.amount.value for transaction in transactions]
        categories = sorted({transaction.category for transaction in transactions})
        statuses = Counter(transaction.status for transaction in transactions)
        dates = sorted(transaction.created_at.date().isoformat() for transaction in transactions)
        currency = transactions[0].amount.currency if transactions else "EUR"
        return {
            "card_token": card_token,
            "transactions_created": len(transactions),
            "summary": {
                "total_amount": {
                    "value": sum(amounts),
                    "currency": currency,
                },
                "categories": categories,
                "statuses": dict(statuses),
                "date_range": f"{dates[0]} to {dates[-1]}" if dates else None,
            },
            "transactions": [transaction.model_dump(mode="json") for transaction in transactions],
            "note": (
                "Sandbox transactions appear as PENDING in the Pliant web app for "
                "1-2 days before booking."
            ),
        }
    except Exception as exc:  # pragma: no cover - defensive tool boundary
        return _tool_error("generate_demo_data", exc)


@mcp.tool(app=AppConfig(resource_uri=CALLBACK_DASHBOARD_URI))
async def diagnose_callbacks(
    card_account_id: str,
    status_filter: str = "FAILED",
    limit: int = 10,
) -> ToolResult:
    """Return callback health data for a card account."""
    try:
        log = await client.get_callback_log(card_account_id)
        subscriptions = await client.get_callback_subscriptions(card_account_id)

        events = log.events
        if status_filter != "ALL":
            events = [event for event in events if event.status == status_filter]
        events = sorted(events, key=lambda event: event.created_at, reverse=True)[:limit]

        payload = {
            "card_account_id": card_account_id,
            "callback_health": {
                "total_events": log.total_events,
                "success_count": log.success_count,
                "failure_count": log.failure_count,
                "success_rate": log.success_rate,
                "circuit_breaker": log.circuit_breaker,
            },
            "subscriptions": [
                {
                    "subscription_id": subscription.id,
                    "event_type": subscription.event_type,
                    "endpoint_url": subscription.endpoint_url,
                    "status": subscription.status,
                }
                for subscription in subscriptions
            ],
            "events": [event.model_dump(mode="json") for event in events],
            "retry_strategy": DEFAULT_CALLBACK_RETRY_STRATEGY,
            "security_note": DEFAULT_CALLBACK_SECURITY_NOTE,
        }
        return _json_result(payload)
    except Exception as exc:  # pragma: no cover - defensive tool boundary
        return _json_result(_tool_error("diagnose_callbacks", exc))


@mcp.resource(
    CONTROLS_CARD_URI,
    app=AppConfig(csp=ResourceCSP(resource_domains=["https://unpkg.com"])),
)
def controls_card() -> str:
    return render_controls_card_html()


@mcp.resource(
    CALLBACK_DASHBOARD_URI,
    app=AppConfig(csp=ResourceCSP(resource_domains=["https://unpkg.com"])),
)
def callback_dashboard() -> str:
    return render_callback_dashboard_html()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
