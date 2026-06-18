"""
BillingCycle — finds due subscriptions, generates invoices, posts ledger DEBITs,
advances the subscription period. Must be IDEMPOTENT (safe to run twice).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Callable, Optional

from billing_engine.db import (
    Database,
    CustomerRepository, PlanRepository, SubscriptionRepository,
    UsageRecordRepository, InvoiceRepository, InvoiceLineItemRepository,
    LedgerRepository,
)
from billing_engine.models import Subscription


@dataclass
class BillingResult:
    invoices_created: int
    invoices_skipped_duplicate: int
    trials_activated: int


class BillingCycle:
    """Day-3 deliverable. Day-4 stretch: add `upgrade_subscription(...)`."""

    def __init__(
        self,
        db: Database,
        customer_repo: CustomerRepository,
        plan_repo: PlanRepository,
        subscription_repo: SubscriptionRepository,
        usage_repo: UsageRecordRepository,
        invoice_repo: InvoiceRepository,
        line_item_repo: InvoiceLineItemRepository,
        ledger_repo: LedgerRepository,
        strategy_factory: Callable,    # given a Plan, returns a PricingStrategy
        discount_factory: Callable,    # given a discount_id or None, returns a Discount or None
        tax_factory: Callable,         # given a Customer, returns (TaxCalculator, TaxContext)
    ) -> None:
        self.db = db
        self.customer_repo = customer_repo
        self.plan_repo = plan_repo
        self.subscription_repo = subscription_repo
        self.usage_repo = usage_repo
        self.invoice_repo = invoice_repo
        self.line_item_repo = line_item_repo
        self.ledger_repo = ledger_repo
        self.strategy_factory = strategy_factory
        self.discount_factory = discount_factory
        self.tax_factory = tax_factory

    # --------------------------------------------------------
    def run(self, as_of: date) -> BillingResult:
        invoices_created = 0
        invoices_skipped_duplicate = 0
        trials_activated = 0

        due_subscriptions = self.subscription_repo.get_due_for_billing(as_of)

        for subscription in due_subscriptions:
            customer = self.customer_repo.get(subscription.customer_id)
            plan = self.plan_repo.get(subscription.plan_id)

            if customer is None or plan is None:
                continue

            strategy = self.strategy_factory(plan)
            discount = self.discount_factory(subscription.discount_id)
            tax_calc, tax_context = self.tax_factory(customer)

            usage_quantity = self.usage_repo.sum_for_period(
                subscription.id,
                "calls",
                subscription.current_period_start,
                subscription.current_period_end,
            )

            invoice_count = self.invoice_repo.count_for_subscription(
                subscription.id
            )

            invoice = build_invoice(
                subscription=subscription,
                plan=plan,
                strategy=strategy,
                discount=discount,
                tax_calc=tax_calc,
                tax_context=tax_context,
                usage_quantity=usage_quantity,
                period_start=subscription.current_period_start,
                period_end=subscription.current_period_end,
                invoice_count_so_far=invoice_count,
            )

            invoice.status = InvoiceStatus.ISSUED

            try:
                saved_invoice = self.invoice_repo.add(invoice)

            except sqlite3.IntegrityError:
                invoices_skipped_duplicate += 1
                continue

            for item in invoice.line_items:
                item.invoice_id = saved_invoice.id
                self.line_item_repo.add(item)

            self.ledger_repo.add(
                LedgerEntry(
                    id=None,
                    invoice_id=saved_invoice.id,
                    customer_id=customer.id,
                    amount=saved_invoice.total,
                    direction=LedgerDirection.DEBIT,
                    reason="Invoice Issued",
                )
            )

            start = subscription.current_period_end

            if plan.billing_period.value == "MONTHLY":
                if start.month == 12:
                    end = start.replace(year=start.year + 1, month=1)
                else:
                    end = start.replace(month=start.month + 1)

            else:  # YEARLY
                end = start.replace(year=start.year + 1)

            self.subscription_repo.update_period(
                subscription.id,
                start,
                end,
            )

            invoices_created += 1

        return BillingResult(
            invoices_created=invoices_created,
            invoices_skipped_duplicate=invoices_skipped_duplicate,
            trials_activated=trials_activated,
        )

    # --------------------------------------------------------
    def upgrade_subscription(self, subscription_id: int, new_plan_id: int, switch_date: date) -> None:
        """Mid-cycle upgrade — Day 4 stretch."""
        # TODO Day 4
        raise NotImplementedError("Day 4: implement BillingCycle.upgrade_subscription")
