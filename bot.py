"""
bot.py — iCloud Verification Code Forwarder Bot

Polls your iCloud inbox every 30 seconds. When a verification/OTP email arrives
(from Twitter, Apple, Instagram, etc.), it immediately sends you the code via Telegram.

VAs see: the code + which Hide My Email alias triggered it.
VAs do NOT see: your real iCloud address.
"""

import asyncio
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from email_monitor import check_new_verification_emails, RECENT_CODES

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN    = os.getenv("TELEGRAM_BOT_TOKEN", "")
ALLOWED_IDS  = [int(x) for x in os.getenv("ALLOWED_USER_IDS", "").split(",") if x.strip()]
RECIPIENT_ID = int(os.getenv("EMAIL_RECIPIENT_ID", ALLOWED_IDS[0] if ALLOWED_IDS else "0"))
POLL_SECS    = int(os.getenv("EMAIL_POLL_INTERVAL", "30"))

IMAP_HOST = os.getenv("IMAP_HOST", "imap.mail.me.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
IMAP_USER = os.getenv("IMAP_USER", "")
IMAP_PASS = os.getenv("IMAP_PASS", "")

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────
def authorized(update: Update) -> bool:
    if not ALLOWED_IDS:
        return True
    return update.effective_user.id in ALLOWED_IDS


def format_code(item: dict) -> str:
    return (
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔐 *VERIFICATION CODE*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏢 Service: *{item['service']}*\n"
        f"📧 Sent to: `{item['to_alias']}`\n"
        f"📨 From: `{item['sender']}`\n"
        f"📋 Subject: {item['subject']}\n\n"
        f"🔑 *Code: `{item['code']}`*\n\n"
        f"⏱ Received: {item['received']}"
    )


# ── Commands ──────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return

    status = "🟢 Active" if IMAP_USER and IMAP_PASS else "🔴 Not configured (set IMAP_USER + IMAP_PASS in .env)"
    text = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📬 *iCloud Code Forwarder*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Email monitor: {status}\n"
        f"Polling every: *{POLL_SECS}s*\n\n"
        "*Commands:*\n"
        "/last\\_codes — Show last 10 codes received\n"
        "/status — Show monitor status\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def last_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return

    if not RECENT_CODES:
        await update.message.reply_text("📭 No codes received yet since bot started.")
        return

    lines = ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "🔐 *LAST 10 CODES*", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━", ""]
    for item in list(RECENT_CODES)[:10]:
        lines.append(
            f"*{item['service']}* — Code: `{item['code']}`\n"
            f"  📧 `{item['to_alias']}`  |  ⏱ {item['received']}\n"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not authorized(update):
        return

    configured = "✅ Configured" if IMAP_USER and IMAP_PASS else "❌ Missing IMAP_USER / IMAP_PASS"
    text = (
        f"*Monitor Status*\n\n"
        f"IMAP: {configured}\n"
        f"Host: `{IMAP_HOST}:{IMAP_PORT}`\n"
        f"User: `{IMAP_USER or 'not set'}`\n"
        f"Poll interval: *{POLL_SECS}s*\n"
        f"Codes in memory: *{len(RECENT_CODES)}*\n"
        f"Sending to: `{RECIPIENT_ID}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ── Background email polling loop ─────────────────────────────────────────────
async def email_polling_loop(bot) -> None:
    logger.info(f"📬 Email monitor started — polling every {POLL_SECS}s")
    while True:
        try:
            loop = asyncio.get_event_loop()
            codes = await loop.run_in_executor(
                None,
                check_new_verification_emails,
                IMAP_HOST, IMAP_USER, IMAP_PASS, IMAP_PORT,
            )
            for item in codes:
                await bot.send_message(
                    chat_id=RECIPIENT_ID,
                    text=format_code(item),
                    parse_mode="Markdown",
                )
        except Exception as e:
            logger.error(f"Polling error: {e}")
        await asyncio.sleep(POLL_SECS)


async def on_startup(application: Application) -> None:
    if IMAP_USER and IMAP_PASS:
        asyncio.create_task(email_polling_loop(application.bot))
    else:
        logger.warning("📭 Email monitor disabled — set IMAP_USER and IMAP_PASS in .env")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(on_startup)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  start))
    app.add_handler(CommandHandler("last_codes", last_codes))
    app.add_handler(CommandHandler("status", status))

    logger.info("🚀 iCloud Code Forwarder Bot starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
