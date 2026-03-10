from __future__ import annotations

import hashlib
import random
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from fixtures import CALLBACK_EVENT_TYPES, CATEGORIES, MERCHANT_FIXTURES
from models import (
    Amount,
    AmountRange,
    CallbackEvent,
    CallbackLog,
    CallbackSubscription,
    Card,
    CardAccount,
    CardControls,
    CardControlsInput,
    Cardholder,
    Merchant,
    Organization,
    ScenarioSummary,
    Transaction,
    TransactionParams,
)


def _hash_text(*parts: str) -> str:
    joined = "::".join(parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def _make_mock_id(prefix: str, *parts: str, length: int = 12) -> str:
    return f"{prefix}_mock_{_hash_text(*parts)[:length]}"


def _make_card_token(*parts: str) -> str:
    value = int(_hash_text(*parts)[:12], 16)
    return str(100_000_000 + (value % 900_000_000))


def _make_uuid(*parts: str) -> str:
    seed = "pliant-demo-architect::" + "::".join(parts)
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, seed))


def _utcnow() -> datetime:
    return datetime.now(UTC)


def split_cardholder_name(full_name: str) -> tuple[str, str]:
    stripped = full_name.strip()
    if not stripped:
        return "Demo", "User"
    if " " not in stripped:
        return stripped, "User"
    first_name, last_name = stripped.rsplit(" ", 1)
    return first_name, last_name


def derive_email(full_name: str) -> str:
    first_name, last_name = split_cardholder_name(full_name)
    email_local = f"{first_name}.{last_name}".replace(" ", ".").lower()
    return f"{email_local}@example.com"


def derive_team(scenario_name: str) -> str:
    parts = scenario_name.split()
    if len(parts) > 1:
        return " ".join(parts[1:])
    return f"{scenario_name} Team"


def derive_last_four(scenario_name: str) -> str:
    return _hash_text(scenario_name)[-4:]


@dataclass(slots=True)
class MockState:
    organizations: dict[str, Organization] = field(default_factory=dict)
    card_accounts: dict[str, CardAccount] = field(default_factory=dict)
    cardholders: dict[str, Cardholder] = field(default_factory=dict)
    cards: dict[str, Card] = field(default_factory=dict)
    cards_by_id: dict[str, Card] = field(default_factory=dict)
    card_controls: dict[str, CardControls] = field(default_factory=dict)
    transactions: dict[str, list[Transaction]] = field(default_factory=dict)
    callback_subscriptions: dict[str, list[CallbackSubscription]] = field(
        default_factory=dict
    )
    callback_log: dict[str, list[CallbackEvent]] = field(default_factory=dict)
    scenarios: dict[str, ScenarioSummary] = field(default_factory=dict)


class MockPliantClient:
    def __init__(self, state: MockState | None = None) -> None:
        self.state = state or MockState()

    def get_card_by_token(self, card_token: str) -> Card:
        try:
            return self.state.cards[card_token]
        except KeyError as exc:
            raise ValueError(f"Unknown card token: {card_token}") from exc

    def get_card_by_id(self, card_id: str) -> Card:
        try:
            return self.state.cards_by_id[card_id]
        except KeyError as exc:
            raise ValueError(f"Unknown card id: {card_id}") from exc

    def get_scenario(self, scenario_name: str) -> ScenarioSummary | None:
        return self.state.scenarios.get(scenario_name)

    async def create_organization(self, name: str) -> Organization:
        organization_id = _make_mock_id("org", name)
        if organization_id in self.state.organizations:
            return self.state.organizations[organization_id]

        organization = Organization(
            id=organization_id,
            name=name,
            status="ACTIVE",
            created_at=_utcnow(),
        )
        self.state.organizations[organization_id] = organization
        return organization

    async def create_card_account(
        self, organization_id: str, name: str, currency: str
    ) -> CardAccount:
        card_account_id = _make_mock_id("ca", organization_id, name, currency)
        if card_account_id in self.state.card_accounts:
            return self.state.card_accounts[card_account_id]

        card_account = CardAccount(
            id=card_account_id,
            organization_id=organization_id,
            name=name,
            currency=currency,
            status="ACTIVE",
            created_at=_utcnow(),
        )
        self.state.card_accounts[card_account_id] = card_account
        return card_account

    async def create_cardholder(
        self,
        organization_id: str,
        name: str,
        email: str,
        team: str | None,
    ) -> Cardholder:
        cardholder_id = _make_mock_id("ch", organization_id, name)
        if cardholder_id in self.state.cardholders:
            return self.state.cardholders[cardholder_id]

        first_name, last_name = split_cardholder_name(name)
        cardholder = Cardholder(
            id=cardholder_id,
            organization_id=organization_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            team=team,
            status="ACTIVE",
            created_at=_utcnow(),
        )
        self.state.cardholders[cardholder_id] = cardholder
        return cardholder

    async def issue_card(
        self,
        card_account_id: str,
        cardholder_id: str,
        currency: str,
        scenario_name: str,
        limit: Amount | None = None,
    ) -> Card:
        card_token = _make_card_token(card_account_id, cardholder_id, scenario_name)
        existing_card = self.state.cards.get(card_token)
        if existing_card is not None:
            return existing_card

        card = Card(
            token=card_token,
            card_id=_make_uuid(card_account_id, cardholder_id, scenario_name),
            card_account_id=card_account_id,
            cardholder_id=cardholder_id,
            last_four=derive_last_four(scenario_name),
            currency=currency,
            card_type="VIRTUAL",
            status="ACTIVE",
            limit=limit,
            created_at=_utcnow(),
        )
        self.state.cards[card.token] = card
        self.state.cards_by_id[card.card_id] = card
        return card

    async def ensure_scenario(
        self,
        scenario_name: str,
        cardholder_name: str,
        card_currency: str,
        card_limit: Amount | None,
    ) -> ScenarioSummary:
        existing = self.get_scenario(scenario_name)
        if existing is not None:
            return existing

        organization = await self.create_organization(scenario_name)
        card_account = await self.create_card_account(
            organization.id,
            f"{scenario_name} card account",
            card_currency,
        )
        cardholder = await self.create_cardholder(
            organization.id,
            cardholder_name,
            derive_email(cardholder_name),
            derive_team(scenario_name),
        )
        card = await self.issue_card(
            card_account.id,
            cardholder.id,
            card_currency,
            scenario_name,
            card_limit,
        )

        summary = ScenarioSummary(
            scenario_name=scenario_name,
            org_id=organization.id,
            card_account_id=card_account.id,
            cardholder_id=cardholder.id,
            card_token=card.token,
            card_id=card.card_id,
            created_at=_utcnow(),
        )
        self.state.scenarios[scenario_name] = summary
        return summary

    async def get_card_controls(self, card_id: str) -> CardControls:
        card = self.get_card_by_id(card_id)
        return self.state.card_controls.get(
            card.token,
            CardControls(card_token=card.token),
        )

    async def set_card_controls(
        self, card_id: str, controls: CardControlsInput
    ) -> CardControls:
        card = self.get_card_by_id(card_id)
        card_controls = CardControls(
            card_token=card.token,
            category_controls=controls.category_controls,
            merchant_controls=controls.merchant_controls,
            time_controls=list(controls.time_controls),
            amount_controls=controls.amount_controls,
        )
        self.state.card_controls[card.token] = card_controls
        return card_controls

    def _allowed_categories_for_card(self, card_token: str) -> list[str]:
        controls = self.state.card_controls.get(card_token)
        if controls is None or controls.category_controls is None:
            return list(CATEGORIES)

        category_controls = controls.category_controls
        if category_controls.restriction == "ALLOWED":
            return list(category_controls.values)

        blocked = set(category_controls.values)
        return [category for category in CATEGORIES if category not in blocked]

    def _blocked_categories_for_card(self, card_token: str) -> list[str]:
        allowed = set(self._allowed_categories_for_card(card_token))
        blocked = [category for category in CATEGORIES if category not in allowed]
        return blocked or ["OTHER"]

    def _build_transaction(
        self,
        card_token: str,
        category: str,
        amount_range: AmountRange,
        merchant_name: str | None,
        status: str,
        seed_parts: tuple[str, ...],
        index: int,
        created_at: datetime,
    ) -> Transaction:
        rng = random.Random(_hash_text(*seed_parts, str(index), status))
        merchant_seed = random.Random(_hash_text(*seed_parts, category, str(index))).choice(
            MERCHANT_FIXTURES[category]
        )
        amount_value = rng.randint(amount_range.minimum, amount_range.maximum)
        merchant = Merchant(
            name=merchant_name or merchant_seed.name,
            category_code=merchant_seed.mcc,
            country=merchant_seed.country,
        )
        transaction_id = _make_mock_id(
            "txn",
            card_token,
            category,
            merchant.name,
            status,
            str(index),
            created_at.isoformat(),
        )
        return Transaction(
            id=transaction_id,
            card_token=card_token,
            amount=Amount(value=amount_value, currency=amount_range.currency),
            merchant=merchant,
            category=category,
            type="PURCHASE",
            status=status,
            created_at=created_at,
        )

    async def generate_transactions(
        self, card_token: str, params: TransactionParams
    ) -> list[Transaction]:
        self.get_card_by_token(card_token)

        amount_range = params.amount_range or AmountRange(min=1000, max=50000, currency="EUR")
        seed_parts = (
            card_token,
            params.category or "random",
            params.merchant_name or "auto",
            params.status,
            str(params.count),
            str(params.include_blocked),
        )
        rng = random.Random(_hash_text(*seed_parts))
        allowed_categories = self._allowed_categories_for_card(card_token)
        blocked_categories = self._blocked_categories_for_card(card_token)

        blocked_count = 0
        if params.include_blocked and params.count > 0:
            blocked_count = 2 if params.count >= 6 else 1

        allowed_count = max(params.count - blocked_count, 0)
        created_now: list[Transaction] = []
        existing_by_id = {txn.id: txn for txn in self.state.transactions.get(card_token, [])}
        start_time = _utcnow()

        for index in range(allowed_count):
            if params.category:
                category = params.category
            else:
                category = rng.choice(allowed_categories)
            created_at = start_time - timedelta(
                days=rng.randint(0, 13),
                hours=rng.randint(0, 23),
                minutes=rng.randint(0, 59),
            )
            transaction = self._build_transaction(
                card_token,
                category,
                amount_range,
                params.merchant_name,
                params.status,
                seed_parts,
                index,
                created_at,
            )
            existing = existing_by_id.get(transaction.id)
            if existing is not None:
                created_now.append(existing)
                continue
            created_now.append(transaction)
            self.state.transactions.setdefault(card_token, []).append(transaction)
            existing_by_id[transaction.id] = transaction

        for offset in range(blocked_count):
            category = blocked_categories[offset % len(blocked_categories)]
            created_at = start_time - timedelta(
                days=rng.randint(0, 13),
                hours=rng.randint(0, 23),
                minutes=rng.randint(0, 59),
            )
            transaction = self._build_transaction(
                card_token,
                category,
                amount_range,
                params.merchant_name,
                "DECLINED",
                seed_parts,
                allowed_count + offset,
                created_at,
            )
            existing = existing_by_id.get(transaction.id)
            if existing is not None:
                created_now.append(existing)
                continue
            created_now.append(transaction)
            self.state.transactions.setdefault(card_token, []).append(transaction)
            existing_by_id[transaction.id] = transaction

        return created_now

    def _seed_callbacks(self, card_account_id: str) -> None:
        if card_account_id in self.state.callback_log:
            return
        card_account = self.state.card_accounts.get(card_account_id)
        if card_account is None:
            raise ValueError(f"Unknown card account id: {card_account_id}")

        subscription = CallbackSubscription(
            id=_make_mock_id("sub", card_account_id),
            card_account_id=card_account_id,
            event_type="TRANSACTION_CREATED",
            endpoint_url="https://acme.com/webhooks/pliant",
            status="ACTIVE",
            signing_key=_make_mock_id("ed25519", card_account_id, length=24),
        )
        self.state.callback_subscriptions[card_account_id] = [subscription]

        organization_id = card_account.organization_id
        related_cards = [
            card for card in self.state.cards.values() if card.card_account_id == card_account_id
        ]
        entity_id = related_cards[0].token if related_cards else card_account_id
        base_time = _utcnow() - timedelta(days=7)
        failed_indices = {3, 12, 18, 27, 41}
        failed_codes = [502, 503, 408, 429, 502]
        events: list[CallbackEvent] = []

        for index in range(47):
            created_at = base_time + timedelta(hours=index * 4)
            is_failed = index in failed_indices
            status = "FAILED" if is_failed else "SENT"
            code = None
            failure_reason = None
            max_retries = 20
            sent_at = created_at + timedelta(minutes=1)
            attempt_count = 1

            if is_failed:
                code = failed_codes.pop(0)
                max_retries = 5 if code == 429 else 20
                attempt_count = 5 if code == 429 else min(5, index % 5 + 1)
                sent_at = None
                failure_reason = (
                    f"{code} response from endpoint after {attempt_count} attempts"
                )

            event = CallbackEvent(
                id=_make_mock_id("cb_evt", card_account_id, str(index)),
                entity_id=entity_id,
                organization_id=organization_id,
                subscription_id=subscription.id,
                event_type=CALLBACK_EVENT_TYPES[index % len(CALLBACK_EVENT_TYPES)],
                status=status,
                http_response_code=code,
                attempt_count=attempt_count,
                max_retries=max_retries,
                endpoint_url=subscription.endpoint_url,
                failure_reason=failure_reason,
                created_at=created_at,
                sent_at=sent_at,
            )
            events.append(event)

        self.state.callback_log[card_account_id] = events

    async def get_callback_log(self, card_account_id: str) -> CallbackLog:
        self._seed_callbacks(card_account_id)
        events = self.state.callback_log[card_account_id]
        subscriptions = self.state.callback_subscriptions[card_account_id]
        success_count = sum(1 for event in events if event.status == "SENT")
        failure_count = sum(1 for event in events if event.status == "FAILED")
        total_events = len(events)
        last_ten = events[-10:]
        last_ten_failures = sum(1 for event in last_ten if event.status == "FAILED")
        circuit_breaker = "OPEN" if last_ten and last_ten_failures / len(last_ten) > 0.5 else "CLOSED"
        success_rate = f"{(success_count / total_events) * 100:.1f}%" if total_events else "0.0%"
        return CallbackLog(
            card_account_id=card_account_id,
            total_events=total_events,
            success_count=success_count,
            failure_count=failure_count,
            success_rate=success_rate,
            circuit_breaker=circuit_breaker,
            subscriptions=subscriptions,
            events=events,
        )

    async def get_callback_subscriptions(
        self, card_account_id: str
    ) -> list[CallbackSubscription]:
        self._seed_callbacks(card_account_id)
        return self.state.callback_subscriptions[card_account_id]
