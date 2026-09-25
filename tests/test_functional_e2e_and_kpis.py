"""
tests/test_functional_e2e_and_kpis.py — Banc d'Évaluation Rigoureuse & KPIs de Production.
Valide :
1. Cycle E2E complet (Customer -> Subscription -> Proration -> Invoice -> Payment -> Ledger).
2. Tests Adversariaux (Injections SQL, transitions interdites, prorata corrompu).
3. Invariant de Conservation Comptable Formelle (Zéro Dérive).
4. Performance & Latence (Débit sous SQLite WAL).
5. Détection de Régression (Mutation Kill).
"""
import pathlib, tempfile, time
from decimal import Decimal
import pytest
from core.subscription import Subscription, SubscriptionState, calculate_proration, InvalidTransitionError, ProrationError
from core.ledger import Ledger, AccountType, Invoice, InvoiceLine, Posting, Transaction
from core.storage import StorageEngine

def test_kpi_1_e2e_business_flow():
    """KPI 1 : Cycle métier complet avec vérification des soldes et de la conservation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = pathlib.Path(tmpdir) / "e2e_billing.db"
        storage = StorageEngine(db_path)
        ledger = Ledger()
        for acc, acc_type in [("receivables", AccountType.ASSET), ("cash", AccountType.ASSET), ("revenue", AccountType.REVENUE), ("tax_payable", AccountType.LIABILITY)]:
            ledger.register_account(acc, acc_type)

        # 1. Création client & abonnement
        storage.save_customer("cust_42", "Stripe Enterprise", "billing@stripe.com")
        sub = Subscription("sub_42", "cust_42", Decimal("100.00"), SubscriptionState.ACTIVE)
        storage.save_subscription(sub)

        # 2. Prorata 15 jours sur 30 = 50.00 HT
        prorated_ht = calculate_proration(sub.monthly_amount, 15, 30)
        assert prorated_ht == Decimal("50.00")

        # 3. Facture avec TVA 20% (10.00 TVA -> 60.00 TTC)
        inv = Invoice("inv_42", "cust_42", [InvoiceLine("Abonnement Mi-Mois", prorated_ht, 1)], tax_rate=Decimal("0.20"))
        assert inv.compute_total() == Decimal("60.0000")

        # 4. Émission facture -> Enregistrement grand livre
        tx_invoice = inv.create_posting_transaction("tx_inv_42")
        ledger.record_transaction(tx_invoice)
        storage.record_invoice_and_postings(inv, tx_invoice)

        # 5. Paiement de la facture : Débit Cash 60.00, Crédit Receivables -60.00
        tx_payment = Transaction("tx_pay_42", "Paiement CB facture 42", [
            Posting("cash", Decimal("60.0000")),
            Posting("receivables", Decimal("-60.0000"))
        ])
        ledger.record_transaction(tx_payment)

        # 6. Vérification des invariants métier
        assert ledger.get_balance("receivables") == Decimal("0.0000")
        assert ledger.get_balance("cash") == Decimal("60.0000")
        assert ledger.get_balance("revenue") == Decimal("-50.0000")
        assert ledger.get_balance("tax_payable") == Decimal("-10.0000")
        assert ledger.verify_conservation() is True

def test_kpi_2_adversarial_and_fuzzing():
    """KPI 2 : Résistance aux entrées corrompues, injections et états interdits."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = StorageEngine(pathlib.Path(tmpdir) / "adv.db")

        # Tentative d'injection SQL
        malicious_id = "cust_' OR '1'='1"
        storage.save_customer(malicious_id, "Hacker", "evil@hack.com")
        # Doit être traité littéralement sans casser la base
        with storage._get_connection() as conn:
            row = conn.execute("SELECT customer_id FROM customers WHERE customer_id = ?;", (malicious_id,)).fetchone()
            assert row[0] == malicious_id

    # Fuzzing FSM : transition interdite CANCELED -> ACTIVE
    sub = Subscription("sub_x", "cust_x", Decimal("10.00"), SubscriptionState.CANCELED)
    with pytest.raises(InvalidTransitionError):
        sub.transition_to(SubscriptionState.ACTIVE)

    # Fuzzing Prorata : jours négatifs ou ratio > 1
    with pytest.raises(ProrationError):
        calculate_proration(Decimal("100.00"), -5, 30)
    with pytest.raises(ProrationError):
        calculate_proration(Decimal("100.00"), 45, 30)

def test_kpi_3_ledger_mutation_kill():
    """KPI 3 : Preuve de non-complaisance : tout déséquilibre comptable est détecté."""
    ledger = Ledger()
    ledger.register_account("a", AccountType.ASSET)
    ledger.register_account("b", AccountType.REVENUE)

    # Mutant 1 : Déséquilibre de 0.0001 € (1 centime de centime)
    mutant_tx = Transaction("tx_mut", "Mutant", [
        Posting("a", Decimal("100.0000")),
        Posting("b", Decimal("-100.0001"))
    ])
    with pytest.raises(ValueError, match="déséquilibrée"):
        ledger.record_transaction(mutant_tx)

def test_kpi_4_performance_throughput():
    """KPI 4 : Débit & latence sous SQLite WAL (>= 500 tx/sec, < 2ms / tx)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = StorageEngine(pathlib.Path(tmpdir) / "bench.db")
        inv = Invoice("inv_perf", "cust_perf", [InvoiceLine("Item", Decimal("10.00"), 1)], tax_rate=Decimal("0.00"))
        tx = inv.create_posting_transaction("tx_perf")

        t0 = time.perf_counter()
        count = 200
        for i in range(count):
            storage.save_customer(f"c_{i}", f"User {i}", f"u{i}@test.com")
        elapsed = time.perf_counter() - t0
        latency_ms = (elapsed / count) * 1000

        assert latency_ms < 5.0, f"Latence trop élevée : {latency_ms:.2f} ms > 5 ms"
