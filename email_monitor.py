"""
email_monitor.py — IMAP verification code monitor.

Connects to an iCloud inbox (or any IMAP server), scans new unread emails,
detects verification / OTP messages, extracts the code, and returns structured
data for the Telegram bot to forward.

iCloud IMAP settings:
  Host : imap.mail.me.com
  Port : 993 (SSL)
  User : your Apple ID email  (e.g. yourname@icloud.com)
  Pass : App-Specific Password — NOT your Apple ID password.
         Generate at: appleid.apple.com → Sign-In & Security → App-Specific Passwords
"""

import imaplib
import email
import re
import logging
from collections import deque
from email.header import decode_header
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

# ── In-memory cache of the last 30 codes ─────────────────────────────────────
RECENT_CODES: deque = deque(maxlen=30)

# ── Patterns to extract codes from email body / subject ──────────────────────
_CODE_PATTERNS = [
    r'(?:verification|confirm|security|login|sign.?in|access|otp|one.?time)[^\d]{0,30}(\d{4,8})',
    r'(?:code|pin)[:\s]+([A-Z0-9]{4,8})',
    r'\b([A-Z0-9]{6,8})\b(?=.*(?:code|verif|confirm))',
    r'\b(\d{6})\b',
    r'\b(\d{4})\b',
]

# ── Keywords that suggest a verification email ────────────────────────────────
_VERIF_KEYWORDS = [
    "verif", "confirm", "otp", "one-time", "security code",
    "login code", "sign-in code", "two-factor", "2fa", "2-step",
    "authentication code", "access code", "your code", "passcode",
    "temporary code", "reset code",
]

# ── Service name mapping by sender domain ─────────────────────────────────────
_SERVICES = {
    "twitter.com":      "🐦 Twitter",
    "x.com":            "🐦 X / Twitter",
    "twimg.com":        "🐦 Twitter",
    "apple.com":        "🍎 Apple",
    "icloud.com":       "🍎 iCloud",
    "google.com":       "🔍 Google",
    "gmail.com":        "📧 Gmail",
    "instagram.com":    "📸 Instagram",
    "facebookmail.com": "🔵 Facebook",
    "meta.com":         "🔵 Meta",
    "onlyfans.com":     "🔞 OnlyFans",
    "telegram.org":     "✈️ Telegram",
    "snapchat.com":     "👻 Snapchat",
    "tiktok.com":       "🎵 TikTok",
    "reddit.com":       "🔴 Reddit",
}


def _decode_header_str(raw) -> str:
    if raw is None:
        return ""
    parts = decode_header(raw)
    out = []
    for decoded, charset in parts:
        if isinstance(decoded, bytes):
            out.append(decoded.decode(charset or "utf-8", errors="replace"))
        else:
            out.append(str(decoded))
    return " ".join(out)


def _extract_body(msg: email.message.Message) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    body += payload.decode("utf-8", errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode("utf-8", errors="replace")
    return body


def _is_verification_email(subject: str, body: str) -> bool:
    combined = (subject + " " + body[:500]).lower()
    return any(kw in combined for kw in _VERIF_KEYWORDS)


def _extract_code(text: str) -> Optional[str]:
    for pattern in _CODE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return matches[0]
    return None


def _identify_service(sender: str) -> str:
    sender_lower = sender.lower()
    for domain, name in _SERVICES.items():
        if domain in sender_lower:
            return name
    match = re.search(r'@([\w.\-]+)', sender)
    return f"📨 {match.group(1)}" if match else sender


def _clean_alias(to_field: str) -> str:
    match = re.search(r'[\w.+\-]+@[\w.\-]+', to_field)
    return match.group(0) if match else to_field


def check_new_verification_emails(
    imap_host: str,
    imap_user: str,
    imap_pass: str,
    imap_port: int = 993,
    folder: str = "INBOX",
) -> List[Dict]:
    """
    Connect to IMAP, process all UNSEEN emails, filter for verification codes.

    Returns a list of dicts:
        {
            "service":   "🐦 Twitter",
            "sender":    "noreply@twitter.com",
            "to_alias":  "abc.def.xyz@privaterelay.appleid.com",
            "subject":   "Your Twitter verification code",
            "code":      "123456",
            "received":  "14:23:05",
        }

    Marks each processed email as SEEN so it won't be re-processed.
    """
    results = []

    try:
        mail = imaplib.IMAP4_SSL(imap_host, imap_port)
        mail.login(imap_user, imap_pass)
        mail.select(folder)

        status, data = mail.search(None, "UNSEEN")
        if status != "OK" or not data[0]:
            mail.logout()
            return []

        ids = data[0].split()
        logger.info(f"📬 {len(ids)} unseen message(s) found")

        for msg_id in ids:
            try:
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    continue

                # msg_data structure can vary — find the bytes payload
                raw_email = None
                for part in msg_data:
                    if isinstance(part, tuple) and isinstance(part[1], bytes):
                        raw_email = part[1]
                        break
                if raw_email is None:
                    continue

                msg = email.message_from_bytes(raw_email)
                subject = _decode_header_str(msg.get("Subject", ""))
                sender  = _decode_header_str(msg.get("From",    ""))
                to_raw  = _decode_header_str(msg.get("To",      ""))
                body    = _extract_body(msg)

                mail.store(msg_id, "+FLAGS", "\\Seen")

                if not _is_verification_email(subject, body):
                    continue

                code    = _extract_code(body) or _extract_code(subject)
                service = _identify_service(sender)
                alias   = _clean_alias(to_raw)
                now     = datetime.now().strftime("%H:%M:%S")

                entry = {
                    "service":  service,
                    "sender":   sender,
                    "to_alias": alias,
                    "subject":  subject[:120],
                    "code":     code or "⚠️ Could not extract — check email manually",
                    "received": now,
                }
                results.append(entry)
                RECENT_CODES.appendleft(entry)

            except Exception as e:
                logger.error(f"Error reading email {msg_id}: {e}")

        mail.logout()

    except imaplib.IMAP4.error as e:
        logger.error(f"IMAP auth/connection error: {e}")
    except OSError as e:
        logger.error(f"IMAP network error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    return results
