---
name: pliant-policy-check
description: Fetch a card's current controls and evaluate a spend scenario in plain language using the structured tool output.
---

# Pliant policy check

Use this skill when the user wants to test whether a spend scenario would be allowed or blocked.

## When to use

- The user asks questions like "Can this cardholder buy X?"
- The user wants to validate a policy live during a demo
- The user wants the current controls explained in business language

## Workflow

1. Call `test_spend_policy` with the `card_token` and the user's scenario text.
2. Use the tool result as the source of truth.
3. State `ALLOWED` or `BLOCKED` clearly.
4. Cite the exact control that caused the outcome.

## Guidance

- Do not invent rules that are not present in the tool output.
- Use `merchant_category_map` to interpret likely merchant categories.
- Consider category, merchant, time, and amount controls together.
- If no restrictions are active, say so explicitly.

## Example prompts

- Can Anna buy a EUR 300 Google Ads subscription on Monday at 10am?
- Can James spend USD 600 on a hotel?
- Explain why this dinner purchase would be blocked.
