from __future__ import annotations

from typing import Protocol

from models import (
    CallbackLog,
    CallbackSubscription,
    Card,
    CardAccount,
    CardControls,
    CardControlsInput,
    Cardholder,
    Organization,
    Transaction,
    TransactionParams,
)


class PliantClient(Protocol):
    async def create_organization(self, name: str) -> Organization: ...

    async def create_card_account(
        self, organization_id: str, name: str, currency: str
    ) -> CardAccount: ...

    async def create_cardholder(
        self,
        organization_id: str,
        name: str,
        email: str,
        team: str | None,
    ) -> Cardholder: ...

    async def issue_card(
        self,
        card_account_id: str,
        cardholder_id: str,
        currency: str,
        scenario_name: str,
    ) -> Card: ...

    async def get_card_controls(self, card_id: str) -> CardControls: ...

    async def set_card_controls(
        self, card_id: str, controls: CardControlsInput
    ) -> CardControls: ...

    async def generate_transactions(
        self, card_token: str, params: TransactionParams
    ) -> list[Transaction]: ...

    async def get_callback_log(self, card_account_id: str) -> CallbackLog: ...

    async def get_callback_subscriptions(
        self, card_account_id: str
    ) -> list[CallbackSubscription]: ...
