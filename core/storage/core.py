"""
core/storage/core.py — Adaptateur de Persistance SQLite WAL Transactionnel (Pure Stdlib).
Garantit l'ACID sans ORM externe et stocke les montants en TEXT pour fidélité Decimal pure.
"""
from decimal import Decimal
import pathlib, sqlite3
from typing import Optional
from core.subscription import Subscription, SubscriptionState
from core.ledger import Invoice, InvoiceStatus, Transaction

class StorageEngine:
    def __init__(self, db_path: pathlib.Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS subscriptions (
                    sub_id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    monthly_amount TEXT NOT NULL,
                    state TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    subtotal TEXT NOT NULL,
                    tax TEXT NOT NULL,
                    total TEXT NOT NULL,
                    status TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS postings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_id TEXT NOT NULL,
                    account_id TEXT NOT NULL,
                    amount TEXT NOT NULL
                );
            """)

    def save_customer(self, customer_id: str, name: str, email: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO customers (customer_id, name, email) VALUES (?, ?, ?);",
                (customer_id, name, email),
            )

    def save_subscription(self, sub: Subscription) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO subscriptions (sub_id, customer_id, monthly_amount, state) VALUES (?, ?, ?, ?);",
                (sub.sub_id, sub.customer_id, str(sub.monthly_amount), sub.state.value),
            )

    def get_subscription(self, sub_id: str) -> Optional[Subscription]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT sub_id, customer_id, monthly_amount, state FROM subscriptions WHERE sub_id = ?;", (sub_id,)).fetchone()
            if not row:
                return None
            return Subscription(
                sub_id=row[0],
                customer_id=row[1],
                monthly_amount=Decimal(row[2]),
                state=SubscriptionState(row[3]),
            )

    def record_invoice_and_postings(self, inv: Invoice, tx: Transaction) -> None:
        """Enregistre atomiquement la facture et ses écritures comptables sous transaction ACID."""
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    "INSERT INTO invoices (invoice_id, customer_id, subtotal, tax, total, status) VALUES (?, ?, ?, ?, ?, ?);",
                    (inv.invoice_id, inv.customer_id, str(inv.compute_subtotal()), str(inv.compute_tax()), str(inv.compute_total()), inv.status.value),
                )
                for p in tx.postings:
                    conn.execute(
                        "INSERT INTO postings (tx_id, account_id, amount) VALUES (?, ?, ?);",
                        (tx.tx_id, p.account_id, str(p.amount)),
                    )
        finally:
            conn.close()

    def get_account_balance(self, account_id: str) -> Decimal:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT amount FROM postings WHERE account_id = ?;", (account_id,)).fetchall()
            return sum((Decimal(r[0]) for r in rows), Decimal("0.0000"))
