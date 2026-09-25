"""
core/ledger/core.py — Grand Livre Comptable à Double Entrée et Moteur de Facturation.
Loi de conservation stricte : sum(debits) + sum(credits) == Decimal('0.0000').
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, List

class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    POSTED = "posted"
    PAID = "paid"
    VOID = "void"

@dataclass(frozen=True)
class Posting:
    account_id: str
    amount: Decimal

@dataclass(frozen=True)
class Transaction:
    tx_id: str
    description: str
    postings: List[Posting]

@dataclass(frozen=True)
class InvoiceLine:
    description: str
    unit_price: Decimal
    quantity: int = 1

    def subtotal(self) -> Decimal:
        return (self.unit_price * Decimal(self.quantity)).quantize(Decimal("0.0001"))

@dataclass
class Invoice:
    invoice_id: str
    customer_id: str
    lines: List[InvoiceLine]
    tax_rate: Decimal = Decimal("0.20")
    discount_amount: Decimal = Decimal("0.0000")
    status: InvoiceStatus = InvoiceStatus.DRAFT

    def compute_subtotal(self) -> Decimal:
        return sum((line.subtotal() for line in self.lines), Decimal("0.0000"))

    def compute_tax(self) -> Decimal:
        net = max(Decimal("0.0000"), self.compute_subtotal() - self.discount_amount)
        return (net * self.tax_rate).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    def compute_total(self) -> Decimal:
        net = max(Decimal("0.0000"), self.compute_subtotal() - self.discount_amount)
        return (net + self.compute_tax()).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    def create_posting_transaction(self, tx_id: str) -> Transaction:
        """Génère la transaction comptable équilibrée : Débit AR = Crédit Revenue + Tax."""
        total = self.compute_total()
        tax = self.compute_tax()
        revenue = total - tax

        postings = [
            Posting(account_id="receivables", amount=total),
            Posting(account_id="revenue", amount=-revenue),
            Posting(account_id="tax_payable", amount=-tax),
        ]
        return Transaction(tx_id=tx_id, description=f"Facture {self.invoice_id}", postings=postings)

class Ledger:
    def __init__(self) -> None:
        self._accounts: Dict[str, AccountType] = {}
        self._balances: Dict[str, Decimal] = {}
        self._txs: Dict[str, Transaction] = {}

    def register_account(self, account_id: str, acc_type: AccountType) -> None:
        if account_id in self._accounts:
            raise ValueError(f"Compte {account_id} déjà existant")
        self._accounts[account_id] = acc_type
        self._balances[account_id] = Decimal("0.0000")

    def record_transaction(self, tx: Transaction) -> None:
        if tx.tx_id in self._txs:
            raise ValueError(f"Transaction dupliquée: {tx.tx_id}")
        if len(tx.postings) < 2:
            raise ValueError("Une transaction requiert au moins 2 écritures")
        total = sum((p.amount for p in tx.postings), Decimal("0.0000"))
        if total != Decimal("0.0000"):
            raise ValueError(f"Transaction déséquilibrée: somme={total} != 0.0000")
        for p in tx.postings:
            if p.account_id not in self._accounts:
                raise ValueError(f"Compte inconnu: {p.account_id}")
        for p in tx.postings:
            self._balances[p.account_id] += p.amount
        self._txs[tx.tx_id] = tx

    def get_balance(self, account_id: str) -> Decimal:
        return self._balances[account_id]

    def verify_conservation(self) -> bool:
        return sum(self._balances.values(), Decimal("0.0000")) == Decimal("0.0000")
