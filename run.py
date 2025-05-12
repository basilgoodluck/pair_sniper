import os
import asyncio
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

async def run_bot():
    print("Initializing bot...")
    await app.initialize()
    print("Starting bot polling...")
    await app.start()
    await app.updater.start_polling()
    print("Bot polling started")
    await app.updater.stop()
    await app.stop()
    await app.shutdown()

def start_server(port):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f"Starting health check server on port {port}...")
    httpd.serve_forever()

def main():
    port = int(os.getenv("PORT", 10000))

    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        print("Shutting down...")
        loop.run_until_complete(app.shutdown())
        server_thread.join()

if __name__ == "__main__":
    main()