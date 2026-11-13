import http.server, socketserver, os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("audio", exist_ok=True)
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
    def guess_type(self, path):
        t = super().guess_type(path)
        return t + "; charset=utf-8" if t.startswith("text/") or t.endswith("javascript") else t
    def do_POST(self):
        m = re.match(r"^/salvar/((?:deg|apo)-\d{2})$", self.path)
        n = int(self.headers.get("Content-Length", 0))
        if not m or n <= 0 or n > 15_000_000:
            self.send_response(400); self.end_headers(); return
        with open(os.path.join("audio", m.group(1) + ".webm"), "wb") as f:
            f.write(self.rfile.read(n))
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", 8080), H) as s:
    print("Pagina de vendas: http://localhost:8080/pagina-de-vendas.html")
    print("Gravador de voz:  http://localhost:8080/gravador.html")
    s.serve_forever()
