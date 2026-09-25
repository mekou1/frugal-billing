"""
tests/test_storage.py — Tests miroir de persistance SQLite WAL.
"""
from decimal import Decimal
import pathlib, tempfile, pytest
from core.storage import StorageEngine
from core.subscription import Subscription, SubscriptionState
from core.ledger import Invoice, InvoiceLine

def test_storage_customer_and_subscription():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = pathlib.Path(tmpdir) / "test_billing.db"
        engine = StorageEngine(db_path)

        engine.save_customer("cust_1", "Alice", "alice@example.com")
        sub = Subscription("sub_1", "cust_1", Decimal("49.99"), SubscriptionState.ACTIVE)
        engine.save_subscription(sub)

        loaded = engine.get_subscription("sub_1")
        assert loaded is not None
        assert loaded.customer_id == "cust_1"
        assert loaded.monthly_amount == Decimal("49.99")
        assert loaded.state == SubscriptionState.ACTIVE

def test_storage_invoice_and_postings_atomic():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = pathlib.Path(tmpdir) / "test_billing.db"
        engine = StorageEngine(db_path)

        line = InvoiceLine("Plan Mensuel", Decimal("100.00"), 1)
        inv = Invoice("inv_1", "cust_1", [line], tax_rate=Decimal("0.20"))
        tx = inv.create_posting_transaction("tx_1")

        engine.record_invoice_and_postings(inv, tx)

        assert engine.get_account_balance("receivables") == Decimal("120.0000")
        assert engine.get_account_balance("revenue") == Decimal("-100.0000")
        assert engine.get_account_balance("tax_payable") == Decimal("-20.0000")

def test_storage_not_found():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = pathlib.Path(tmpdir) / "test_billing.db"
        engine = StorageEngine(db_path)
        assert engine.get_subscription("non_existent") is None
