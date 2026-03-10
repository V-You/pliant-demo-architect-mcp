from __future__ import annotations

from dataclasses import dataclass


CATEGORIES = [
    "ADVERTISING_AND_MARKETING",
    "COMPUTING_AND_SOFTWARE",
    "EDUCATION_AND_TRAINING",
    "ELECTRONICS_AND_IT_EQUIPMENT",
    "ENTERTAINMENT_AND_WELLNESS",
    "FOOD_AND_DRINKS",
    "GIFTS_AND_VOUCHERS",
    "MATERIALS_AND_PACKAGING",
    "OFFICE_SUPPLIES_AND_EQUIPMENT",
    "SERVICES",
    "TRAVEL_AND_ACCOMMODATION",
    "OTHER",
]


CATEGORY_LABELS = {
    "ADVERTISING_AND_MARKETING": "Advertising & Marketing",
    "COMPUTING_AND_SOFTWARE": "Computing & Software",
    "EDUCATION_AND_TRAINING": "Education & Training",
    "ELECTRONICS_AND_IT_EQUIPMENT": "Electronics & IT Equipment",
    "ENTERTAINMENT_AND_WELLNESS": "Entertainment & Wellness",
    "FOOD_AND_DRINKS": "Food & Drinks",
    "GIFTS_AND_VOUCHERS": "Gifts & Vouchers",
    "MATERIALS_AND_PACKAGING": "Materials & Packaging",
    "OFFICE_SUPPLIES_AND_EQUIPMENT": "Office Supplies & Equipment",
    "SERVICES": "Services",
    "TRAVEL_AND_ACCOMMODATION": "Travel & Accommodation",
    "OTHER": "Other",
}


@dataclass(frozen=True)
class MerchantSeed:
    name: str
    mcc: str
    country: str


MERCHANT_FIXTURES: dict[str, tuple[MerchantSeed, ...]] = {
    "ADVERTISING_AND_MARKETING": (
        MerchantSeed("Google Ads", "7311", "DE"),
        MerchantSeed("Meta Business", "7311", "IE"),
        MerchantSeed("LinkedIn Ads", "7311", "US"),
        MerchantSeed("HubSpot", "7312", "US"),
    ),
    "COMPUTING_AND_SOFTWARE": (
        MerchantSeed("AWS", "5734", "DE"),
        MerchantSeed("GitHub", "7372", "US"),
        MerchantSeed("Atlassian", "7372", "DE"),
        MerchantSeed("Datadog", "7372", "US"),
        MerchantSeed("Vercel", "7372", "US"),
    ),
    "EDUCATION_AND_TRAINING": (
        MerchantSeed("Coursera", "8299", "US"),
        MerchantSeed("Udemy", "8299", "US"),
        MerchantSeed("LinkedIn Learning", "8299", "US"),
        MerchantSeed("Pluralsight", "8211", "US"),
    ),
    "ELECTRONICS_AND_IT_EQUIPMENT": (
        MerchantSeed("Apple Store", "5732", "DE"),
        MerchantSeed("Dell", "5734", "DE"),
        MerchantSeed("MediaMarkt", "5732", "DE"),
        MerchantSeed("Best Buy", "5732", "US"),
    ),
    "ENTERTAINMENT_AND_WELLNESS": (
        MerchantSeed("Spotify", "4899", "SE"),
        MerchantSeed("Headspace", "7991", "US"),
        MerchantSeed("Netflix", "4899", "NL"),
    ),
    "FOOD_AND_DRINKS": (
        MerchantSeed("Deliveroo", "5814", "DE"),
        MerchantSeed("Starbucks", "5814", "DE"),
        MerchantSeed("DoorDash", "5812", "US"),
    ),
    "GIFTS_AND_VOUCHERS": (
        MerchantSeed("Amazon Gift Cards", "5947", "DE"),
        MerchantSeed("Cadooz", "5947", "DE"),
        MerchantSeed("Wunschgutschein", "5947", "DE"),
    ),
    "MATERIALS_AND_PACKAGING": (
        MerchantSeed("Uline", "5085", "US"),
        MerchantSeed("Rajapack", "5169", "DE"),
        MerchantSeed("Viking Direct", "5169", "DE"),
    ),
    "OFFICE_SUPPLIES_AND_EQUIPMENT": (
        MerchantSeed("Staples", "5943", "DE"),
        MerchantSeed("Viking", "5943", "DE"),
        MerchantSeed("IKEA Business", "5944", "DE"),
    ),
    "SERVICES": (
        MerchantSeed("McKinsey", "7392", "DE"),
        MerchantSeed("Deloitte", "7392", "DE"),
        MerchantSeed("WeWork", "7399", "DE"),
        MerchantSeed("Fiverr", "7399", "IL"),
    ),
    "TRAVEL_AND_ACCOMMODATION": (
        MerchantSeed("Lufthansa", "3000", "DE"),
        MerchantSeed("Booking.com", "7011", "NL"),
        MerchantSeed("Marriott", "7011", "US"),
        MerchantSeed("Uber", "4121", "DE"),
    ),
    "OTHER": (
        MerchantSeed("Miscellaneous merchant", "5999", "DE"),
        MerchantSeed("Unknown vendor", "5999", "US"),
    ),
}


CALLBACK_EVENT_TYPES = (
    "TRANSACTION_CREATED",
    "CARD_STATUS_CHANGED",
    "CARD_CONTROLS_UPDATED",
)


DEFAULT_CALLBACK_RETRY_STRATEGY = {
    "4xx_errors": "~5 retries with exponential backoff",
    "other_errors": "~20 retries with exponential backoff",
    "circuit_breaker": "Opens after sustained failures, auto-recovers",
}


DEFAULT_CALLBACK_SECURITY_NOTE = (
    "Callbacks are signed using Ed25519 via the Standard Webhooks spec. "
    "Consumers should verify the X-Webhook-Signature header using the signing "
    "key from their callback subscription."
)


def merchant_names_by_category() -> dict[str, list[str]]:
    return {
        category: [merchant.name for merchant in merchants]
        for category, merchants in MERCHANT_FIXTURES.items()
    }
