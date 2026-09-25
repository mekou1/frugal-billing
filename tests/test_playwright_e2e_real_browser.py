"""
tests/test_playwright_e2e_real_browser.py — Test Navigateur Réel Playwright E2E.
Exécute le parcours utilisateur complet sur Google Chrome headless :
1. Démarrage du serveur FrugalBilling.
2. Chargement de la page d'accueil et des badges d'invariants.
3. Création interactive d'un abonnement via le DOM.
4. Vérification de la mise à jour dynamique des compteurs et du tableau.
5. Résiliation et vérification du badge CANCELED.
"""
import threading, time, pytest
from playwright.sync_api import sync_playwright
from launcher import run_server

PORT = 8197

@pytest.fixture(scope="module", autouse=True)
def live_server():
    server_thread = threading.Thread(target=run_server, args=(PORT,), daemon=True)
    server_thread.start()
    time.sleep(0.2)
    yield

def test_browser_e2e_subscription_lifecycle():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--disable-gpu"]
        )
        page = browser.new_page()
        page.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="networkidle")

        # 1. Vérification du titre et des badges
        assert "FrugalBilling" in page.title()
        assert "SQLite WAL" in page.inner_text("body")
        assert "Zero-Token Engine" in page.inner_text("body")

        # 2. Vérification des métriques initiales
        assert "349.00 €" in page.inner_text("#val-mrr")
        assert page.inner_text("#val-subs") == "4"

        # 3. Remplissage du formulaire et soumission
        page.fill("#cust-name", "Anthropic Enterprise")
        page.fill("#sub-amount", "499.00")
        page.click("button:has-text('Souscrire Immédiatement')")

        # 4. Vérification de la mise à jour dynamique
        assert page.inner_text("#val-subs") == "5"
        assert "Anthropic Enterprise" in page.inner_text("#sub-tbody")
        assert "499.00 €" in page.inner_text("#sub-tbody")
        assert "249.50 €" in page.inner_text("#sub-tbody")  # Prorata 15j

        # 5. Résiliation de l'abonnement
        last_row = page.locator("#sub-tbody tr:last-child")
        last_row.locator("button:has-text('Résilier')").click()
        assert "CANCELED" in last_row.inner_text()

        browser.close()
