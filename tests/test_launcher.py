"""
tests/test_launcher.py — Tests de l'API et du cockpit FrugalBilling.
"""
import json, urllib.request, threading, time
from launcher import run_server

def test_api_health_and_metrics():
    # Lance le serveur sur un port dédié dans un thread
    port = 8199
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    time.sleep(0.1)

    # Test /api/health
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data["status"] == "ok"
        assert data["app"] == "FrugalBilling"

    # Test /api/metrics
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/metrics") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data["mrr"] == "349.00"
        assert data["status"] == "BALANCED_ACID"
