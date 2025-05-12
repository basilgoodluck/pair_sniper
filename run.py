import os
import asyncio
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder
from core.config import tg_bot_token, backend_url
from bot.register_handlers import register_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            logger.warning("Invalid content-type")
            self.send_response(400)
            self.end_headers()
            return

        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            logger.warning("Empty request body")
            self.send_response(400)
            self.end_headers()
            return

        update_data = self.rfile.read(content_length).decode('utf-8')
        try:
            update_json = json.loads(update_data)
            update = Update.de_json(update_json, app.bot)
            if update is None:
                logger.error("Failed to parse update: Update object is None")
                self.send_response(400)
                self.end_headers()
                return
            logger.info(f"Received update: {update.update_id}")
            asyncio.run_coroutine_threadsafe(app.process_update(update), asyncio.get_event_loop())
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON data: {str(e)}")
            self.send_response(400)
            self.end_headers()
            return
        except Exception as e:
            logger.error(f"Error processing update: {str(e)}")
            self.send_response(500)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()

async def set_webhook():
    port = int(os.getenv("PORT", 10000))
    public_url = os.getenv("RENDER_EXTERNAL_URL", backend_url)
    if not public_url.startswith("https://"):
        raise ValueError("Webhook URL must use HTTPS. Check backend_url or RENDER_EXTERNAL_URL.")
    webhook_url = f"{public_url}{WEBHOOK_PATH}"

    logger.info(f"Setting webhook to {webhook_url}")
    await app.bot.set_webhook(url=webhook_url)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.initialize())
    loop.run_until_complete(set_webhook())

    port = int(os.getenv("PORT", 10000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, WebhookHandler)
    logger.info(f"Starting server on port {port}")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        httpd.server_close()
        loop.run_until_complete(app.shutdown())

if __name__ == "__main__":
    main()