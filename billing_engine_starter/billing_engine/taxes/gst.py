"""
GSTCalculator — Indian Goods & Services Tax.

The rule:
    - If customer_state == seller_state (or seller_state is "")  =>  intra-state
        -> charge CGST + SGST (split equally, e.g. 9% + 9% = 18%)
    - Else  =>  inter-state
        -> charge IGST (e.g. 18%)

Customers without a state code default to IGST (safe choice).
"""

from decimal import decimal
from billing_engine.money import Money
from billing_engine.taxes.base import (
    TaxCalculator,
    TaxContext,
    TaxBreakdown,
)


class GSTCalculator(TaxCalculator):
    def __init__(
        self,
        cgst: Decimal,
        sgst: Decimal,
        igst: Decimal,
    ) -> None:
# TODO Day 1
        #   - Validate each rate is Decimal in [0, 1].
        #   - Validate cgst + sgst == igst (sanity check on Indian GST setup).
        #   - Store on self.
        for rate in (cgst, sgst, igst):
            if isinstance(rate, float):
                raise TypeError("Use Decimal, not float")

            if rate < Decimal("0") or rate > Decimal("1"):
                raise ValueError("GST rates must be between 0 and 1")

        if cgst + sgst != igst:
            raise ValueError(
                "Invalid GST setup: cgst + sgst must equal igst"
            )

        self.cgst = cgst
        self.sgst = sgst
        self.igst = igst

    def apply(
        self,
        taxable: Money,
        context: TaxContext,
    ) -> TaxBreakdown:
 # TODO Day 1
        #   - Decide intra vs inter-state from context.
        #     intra = bool(context.customer_state) and context.customer_state == context.seller_state
        #   - If intra: components = [("CGST X%", taxable*cgst), ("SGST Y%", taxable*sgst)], total = sum
        #   - Else:     components = [("IGST Z%", taxable*igst)],                            total = igst leg
        
        intra = (
            bool(context.customer_state)
            and context.customer_state == context.seller_state
        )

        if intra:
            cgst_amt = taxable * self.cgst
            sgst_amt = taxable * self.sgst

            return TaxBreakdown(
                components=[
                    (
                        f"CGST {(self.cgst * Decimal('100')).normalize()}%",
                        cgst_amt,
                    ),
                    (
                        f"SGST {(self.sgst * Decimal('100')).normalize()}%",
                        sgst_amt,
                    ),
                ],
                total=cgst_amt + sgst_amt,
            )

        igst_amt = taxable * self.igst

        return TaxBreakdown(
            components=[
                (
                    f"IGST {(self.igst * Decimal('100')).normalize()}%",
                    igst_amt,
                )
            ],
            total=igst_amt,
        )
        
