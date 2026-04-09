# 📬 iCloud Verification Code Forwarder

A lightweight Telegram bot that watches your iCloud inbox and instantly forwards verification/OTP codes to Telegram — without exposing your real email address to anyone.

**Perfect for teams using iCloud Hide My Email** — VAs see the code and which alias triggered it, never your actual address.

---

## How it works

```
iCloud Hide My Email alias  →  your main iCloud inbox  →  Telegram bot  →  you (or your team)
```

1. You create unique **Hide My Email** aliases in iCloud (one per account/service)
2. All verification emails land in your main iCloud inbox
3. This bot polls the inbox every 30 seconds
4. When it spots a verification email, it extracts the code and fires it to Telegram
5. Your team sees the code — not your real email

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourname/icloud-code-forwarder.git
cd icloud-code-forwarder
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create your bot
- Open Telegram → message **@BotFather**
- `/newbot` → follow the steps → copy your token

### 4. Get your Telegram user ID
- Message **@userinfobot** → it replies with your user ID

### 5. Generate an App-Specific Password
> ⚠️ iCloud requires this — your Apple ID password **will not work** with IMAP apps.

1. Go to [appleid.apple.com](https://appleid.apple.com)
2. Sign-In & Security → **App-Specific Passwords**
3. Click `+` → name it (e.g. `Code Forwarder`) → copy the password

### 6. Configure
```bash
cp .env.example .env
```

Edit `.env`:
```env
TELEGRAM_BOT_TOKEN=7xxxxxxxxx:AAF...
ALLOWED_USER_IDS=123456789
EMAIL_RECIPIENT_ID=123456789

IMAP_HOST=imap.mail.me.com
IMAP_PORT=993
IMAP_USER=yourname@icloud.com
IMAP_PASS=xxxx-xxxx-xxxx-xxxx
```

### 7. Run
```bash
python bot.py
```

---

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Show status and help |
| `/last_codes` | Show last 10 codes received (since bot started) |
| `/status` | Show IMAP connection status |

---

## What a code notification looks like

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔐 VERIFICATION CODE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏢 Service: 🐦 Twitter
📧 Sent to: orange.cloud.abc123@privaterelay.appleid.com
📨 From: noreply@twitter.com
📋 Subject: Your Twitter confirmation code

🔑 Code: 847291

⏱ Received: 14:23:05
```

---

## Supported services

Automatically recognises emails from: Twitter/X, Apple, Google, Instagram, Facebook, OnlyFans, Snapchat, TikTok, Reddit, Telegram, and more. Falls back to the sender's domain for anything else.

---

## Requirements

- Python 3.9+
- An iCloud account with IMAP enabled
- A Telegram bot token from @BotFather

No external dependencies for the email logic — uses Python's built-in `imaplib` and `email` modules.
