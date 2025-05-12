import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import ApplicationBuilder
from core.config import tg_bot_token
from bot.register_handlers import register_handlers

app = ApplicationBuilder().token(tg_bot_token).build()
register_handlers(app)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running")

def start_server(port):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f"Health check server running on port {port}")
    httpd.serve_forever()

def main():
    port = int(os.getenv("PORT", 10000))
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()
    app.run_polling()

if __name__ == "__main__":
    main()
