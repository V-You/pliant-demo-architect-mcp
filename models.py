from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Amount(BaseModel):
    value: int
    currency: str


class Organization(BaseModel):
    id: str
    name: str
    status: str
    created_at: datetime


class CardAccount(BaseModel):
    id: str
    organization_id: str
    name: str
    currency: str
    status: str
    created_at: datetime


class Cardholder(BaseModel):
    id: str
    organization_id: str
    first_name: str
    last_name: str
    email: str
    team: str | None
    status: str
    created_at: datetime


class Card(BaseModel):
    token: str
    card_id: str
    card_account_id: str
    cardholder_id: str
    last_four: str
    currency: str
    card_type: str
    status: str
    limit: Amount | None
    created_at: datetime


class CategoryControls(BaseModel):
    type: str = "CATEGORY"
    values: list[str]
    restriction: str


class MerchantControls(BaseModel):
    type: str
    values: list[str]
    restriction: str


class TimeControl(BaseModel):
    days: list[str]
    start_time: str
    end_time: str
    timezone: str


class PeriodicLimit(BaseModel):
    amount: Amount
    period: str


class AmountControls(BaseModel):
    per_transaction: Amount | None = None
    periodic: PeriodicLimit | None = None


class CardControls(BaseModel):
    card_token: str
    category_controls: CategoryControls | None = None
    merchant_controls: MerchantControls | None = None
    time_controls: list[TimeControl] = Field(default_factory=list)
    amount_controls: AmountControls | None = None


class Merchant(BaseModel):
    name: str
    category_code: str
    country: str


class Transaction(BaseModel):
    id: str
    card_token: str
    amount: Amount
    merchant: Merchant
    category: str
    type: str
    status: str
    created_at: datetime


class CallbackSubscription(BaseModel):
    id: str
    card_account_id: str
    event_type: str
    endpoint_url: str
    status: str
    signing_key: str


class CallbackEvent(BaseModel):
    id: str
    entity_id: str
    organization_id: str
    subscription_id: str
    event_type: str
    status: str
    http_response_code: int | None
    attempt_count: int
    max_retries: int
    endpoint_url: str
    failure_reason: str | None
    created_at: datetime
    sent_at: datetime | None


class CallbackLog(BaseModel):
    card_account_id: str
    total_events: int
    success_count: int
    failure_count: int
    success_rate: str
    circuit_breaker: str
    subscriptions: list[CallbackSubscription]
    events: list[CallbackEvent]


class ScenarioSummary(BaseModel):
    scenario_name: str
    org_id: str
    card_account_id: str
    cardholder_id: str
    card_token: str
    card_id: str
    created_at: datetime


class AmountRange(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    minimum: int = Field(alias="min")
    maximum: int = Field(alias="max")
    currency: str = "EUR"


class CardControlsInput(BaseModel):
    category_controls: CategoryControls | None = None
    merchant_controls: MerchantControls | None = None
    time_controls: list[TimeControl] = Field(default_factory=list)
    amount_controls: AmountControls | None = None


class TransactionParams(BaseModel):
    count: int = 5
    category: str | None = None
    amount_range: AmountRange | None = None
    merchant_name: str | None = None
    status: str = "CONFIRMED"
    include_blocked: bool = False
