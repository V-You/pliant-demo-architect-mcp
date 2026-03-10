---
name: pliant-demo-prep
description: Prepare a full mock Pliant demo scenario, apply card controls, and populate realistic transactions for a prospect demo.
---

# Pliant demo prep

Use this skill when the user wants a demo environment prepared quickly for a prospect call.

## When to use

- The user asks to prepare or set up a demo for a prospect
- The user wants an org, cardholder, card controls, and transactions created in one flow
- The user gives business requirements like categories, hours, or transaction limits rather than raw tool arguments

## Workflow

1. Call `setup_demo_scenario` first.
2. Translate the user's control requirements into `set_card_controls` inputs.
3. Call `generate_demo_data` with realistic defaults if the user does not specify exact counts or categories.
4. Summarize the resulting scenario, card token, controls, and transaction mix.

## Defaults to use when details are missing

- `card_currency`: `EUR`
- `card_limit`: `{"value": 500000, "currency": "EUR"}`
- `count`: `5`
- `status`: `CONFIRMED`
- `include_blocked`: `false`

## Guidance

- Keep the flow simple and deterministic.
- Use `allowed_categories` or `blocked_categories`, never both.
- Prefer `per_transaction_limit` unless the user explicitly asks for a periodic limit.
- If the user asks for a natural language walkthrough, summarize the result in business terms, not just raw JSON.

## Example prompts

- Set up a demo scenario for Adidas EU Marketing with Anna Schmidt, EUR card, and a 5000 EUR limit.
- Add card controls for advertising and software only, weekdays 08:00 to 18:00 Europe/Berlin, and a 2000 EUR max per transaction.
- Generate 8 realistic transactions and include 2 declined attempts.
