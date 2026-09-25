"""
launcher.py — Serveur HTTP & Cockpit Visual FrugalBilling (Pure Stdlib Python).
Zéro dépendance externe, écoute sur le port 8092 par défaut.
"""
import http.server, json, pathlib, socketserver, sys

PORT = 8092
ROOT_DIR = pathlib.Path(__file__).resolve().parent
PUBLIC_DIR = ROOT_DIR / "public"

class FrugalHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self._send_json(200, {"status": "ok", "app": "FrugalBilling", "engine": "SQLite-WAL"})
        elif self.path == "/api/metrics":
            self._send_json(200, {
                "mrr": "349.00",
                "active_subscriptions": 4,
                "conservation_invariant": "0.0000",
                "status": "BALANCED_ACID"
            })
        else:
            super().do_GET()

    def _send_json(self, status: int, data: dict) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

def run_server(port: int = PORT) -> None:
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), FrugalHandler) as httpd:
        print(f"🚀 FrugalBilling Cockpit lancé sur http://127.0.0.1:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Arrêt propre du cockpit.")

if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(p)
