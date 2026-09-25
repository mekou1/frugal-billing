"""
tests/test_ledger.py — Tests miroir du grand livre et moteur de facturation.
"""
from decimal import Decimal
import pytest
from core.ledger import (
    AccountType,
    Invoice,
    InvoiceLine,
    InvoiceStatus,
    Ledger,
    Posting,
    Transaction,
)

def test_invoice_totals_computation():
    line1 = InvoiceLine("Abonnement Pro", Decimal("100.00"), 1)
    line2 = InvoiceLine("Siège additionnel", Decimal("20.00"), 2)
    inv = Invoice(
        invoice_id="inv_101",
        customer_id="cust_1",
        lines=[line1, line2],
        tax_rate=Decimal("0.20"),
        discount_amount=Decimal("10.00"),
    )
    # subtotal = 100 + 40 = 140.00
    assert inv.compute_subtotal() == Decimal("140.0000")
    # net = 140 - 10 = 130.00 -> tax = 130 * 0.20 = 26.00
    assert inv.compute_tax() == Decimal("26.0000")
    # total = 130 + 26 = 156.00
    assert inv.compute_total() == Decimal("156.0000")

def test_ledger_recording_and_conservation():
    ledger = Ledger()
    ledger.register_account("receivables", AccountType.ASSET)
    ledger.register_account("revenue", AccountType.REVENUE)
    ledger.register_account("tax_payable", AccountType.LIABILITY)

    line = InvoiceLine("Plan Mensuel", Decimal("100.00"), 1)
    inv = Invoice("inv_102", "cust_1", [line], tax_rate=Decimal("0.20"))
    tx = inv.create_posting_transaction("tx_001")

    ledger.record_transaction(tx)
    assert ledger.get_balance("receivables") == Decimal("120.0000")
    assert ledger.get_balance("revenue") == Decimal("-100.0000")
    assert ledger.get_balance("tax_payable") == Decimal("-20.0000")
    assert ledger.verify_conservation() is True

def test_ledger_rejects_unbalanced_transaction():
    ledger = Ledger()
    ledger.register_account("acc1", AccountType.ASSET)
    ledger.register_account("acc2", AccountType.REVENUE)

    unbalanced_tx = Transaction(
        tx_id="tx_err",
        description="Fausse écriture",
        postings=[
            Posting("acc1", Decimal("100.0000")),
            Posting("acc2", Decimal("-99.0000")),
        ],
    )
    with pytest.raises(ValueError, match="déséquilibrée"):
        ledger.record_transaction(unbalanced_tx)
