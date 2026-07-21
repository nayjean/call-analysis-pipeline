# Intent Taxonomy Reference

Derived from two internal Arinox/client data sources (Mar-Apr 2026): an outbound call log (~6,500 calls) and a customer support ticket system (~2,655 tickets). Both were used **only in aggregate** (category names and counts) — no personal data, phone numbers, names, or message content was extracted or retained. Source files were deleted after this extraction.

## Support ticket categories (top-level, by volume)

| Category | Count |
|---|---|
| Order Shipping | 372 |
| Defect | 340 |
| OutBound | 339 |
| Order Creating | 262 |
| Return Creation | 179 |
| Refund | 178 |
| Return Shipping | 161 |
| Store Related | 149 |
| Alteration | 99 |
| Cancellation | 94 |
| Exchange | 93 |
| Order Delivery | 59 |
| Loyalty Programme | 56 |
| Store Billing | 55 |
| Product Related | 40 |

## Notable sub-categories

Order Status, Product Query, Return Refund Status, Shipping Delay, Store Information, Color Fade, Not Able to Cancel, Stitching Issue, Unable to Initiate Return, Delay in Pick Up, Lints, Process & TAT.

## Call log observations

- Majority of the outbound call campaign's usable comments indicated sales/retention-style outcomes: "Not interested", "cb" (callback requested), "Follow up tomorrow", "Language Barrier" — confirming these are not purely inbound complaint calls.
- `Disposition` field was mostly operational (wrap-up time flags), not a usable intent taxonomy on its own.

## Resulting candidate intents for `intent.py`

Condensed from the above into a manageable zero-shot classification set:

- order or shipping status
- return or refund request
- product defect complaint
- exchange or alteration request
- cancellation request
- store related inquiry
- not interested / callback requested
- general inquiry

This list is grounded in real observed categories rather than a generic guess, though it should still be validated against more real calls during Phase 6 testing.
