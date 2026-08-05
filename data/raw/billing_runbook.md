# Billing Runbook

Owner: Billing Engineering  
Last updated: 2026-07-30

## Invoice Generation

Invoices are generated daily at 02:00 UTC. The billing worker reads active subscriptions, calculates usage, applies discounts, and writes invoice records to the billing database.

## Failed Payment Handling

When a payment fails, the customer enters dunning status. The system retries payment after 1 day, 3 days, and 7 days. After the third failed retry, the subscription is marked past due.

## Manual Invoice Regeneration

Support engineers can regenerate an invoice from the Billing Admin Console. Select the customer account, open the invoice history tab, choose the invoice, and click Regenerate.

## Common Billing Errors

BILLING_409_DUPLICATE_INVOICE means an invoice already exists for the selected billing period.
BILLING_422_INVALID_TAX_ID means the provided tax identifier failed validation.
BILLING_503_PROVIDER_DOWN means the external payment provider is unavailable.

## Escalation

Escalate to Billing Engineering if invoice regeneration fails twice or if a customer reports incorrect tax calculation.
