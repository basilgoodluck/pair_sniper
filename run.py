import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder
from core.config import tg_bot_token, backend_url
from bot.register_handlers import register_handlers

app = ApplicationBuilder().token(tg_bot_token).build()
register_handlers(app)

WEBHOOK_PATH = "/webhook"

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != WEBHOOK_PATH:
            self.send_response(404)
            self.end_headers()
            return

        if 'content-type' not in self.headers or self.headers['content-type'] != 'application/json':
            self.send_response(400)  
            self.end_headers()
            return

        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_response(400)
            self.end_headers()
            return

        update_data = self.rfile.read(content_length).decode('utf-8')
        try:
            update = Update.de_json(eval(update_data), app.bot) 
        except (SyntaxError, ValueError, TypeError):
            self.send_response(400)  
            self.end_headers()
            return
        
        asyncio.run_coroutine_threadsafe(app.process_update(update), asyncio.get_event_loop())
        self.send_response(200)
        self.end_headers()

async def set_webhook():
    port = int(os.getenv("PORT", 10000)) 
    public_url = backend_url
    webhook_url = f"{public_url}{WEBHOOK_PATH}"

    print(f"Setting webhook to {webhook_url}")
    await app.bot.set_webhook(url=webhook_url)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.initialize())
    loop.run_until_complete(set_webhook())

    port = int(os.getenv("PORT", 10000)) 
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, WebhookHandler)
    print(f"Starting server on port {port}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
        httpd.server_close()
        loop.run_until_complete(app.shutdown())

if __name__ == "__main__":
    main()