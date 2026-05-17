# 📬 iCloud Verification Code Forwarder

A Telegram bot that watches your iCloud inbox and instantly forwards verification/OTP codes to you via Telegram — without exposing your real email address to anyone.

**Perfect for teams using iCloud Hide My Email** — you (or your VAs) see the code and which alias triggered it, never your actual iCloud address.

---

## How It Works (Big Picture)

```
Service sends verification email
        ↓
Lands in your iCloud inbox
        ↓
This bot polls the inbox every 30 seconds
        ↓
Detects the code, identifies the service
        ↓
Sends it to your Telegram instantly
```

1. You create unique **Hide My Email** aliases in iCloud (one per account/service).
2. All verification emails land in your main iCloud inbox.
3. This bot checks for new unread emails every 30 seconds.
4. When it spots a verification email (Twitter, OnlyFans, Google, etc.), it extracts the code.
5. It sends a formatted message to your Telegram with the code, which service it's from, and which alias received it.

---

## What You'll Need Before Starting

| Item | Where to get it | Notes |
|------|----------------|-------|
| A computer | Any Mac, Windows, or Linux machine | Or a VPS / server to run 24/7 |
| Python 3.9+ | [python.org](https://www.python.org/downloads/) | Check with `python3 --version` |
| An iCloud account | You already have one if you use an iPhone/Mac | Must have 2FA enabled |
| A Telegram account | [telegram.org](https://telegram.org) | Free |
| A text editor | VS Code, Cursor, or even Notepad | Anything works |
| Git (optional) | [git-scm.com](https://git-scm.com) | To clone the repo |

---

## A-Z Setup Guide

### Step 1: Install Python

> If you already have Python 3.9+, skip this step.

**Mac:**
```bash
brew install python
```

**Windows:**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download the latest version (3.11 or 3.12)
3. **CHECK THE BOX** that says "Add Python to PATH" during install — this is critical
4. Click Install

**Verify it works:**
```bash
python3 --version
# Should print: Python 3.11.x or similar
```

---

### Step 2: Download This Project

**Option A — Using Git (recommended):**
```bash
git clone https://github.com/sku-tny/forwarder.git
cd forwarder
```

**Option B — Manual download:**
1. Go to the GitHub repo
2. Click the green "Code" button → "Download ZIP"
3. Unzip it somewhere you'll remember (e.g. your Desktop)
4. Open a terminal and `cd` into that folder

---

### Step 3: Install Python Dependencies

Open your terminal in the project folder and run:

```bash
pip install -r requirements.txt
```

> **Windows users:** If `pip` doesn't work, try `pip3` instead. If neither works, try `python -m pip install -r requirements.txt`

This installs two packages:
- `python-telegram-bot` — the library that connects to Telegram
- `python-dotenv` — reads your `.env` config file

---

### Step 4: Create a Telegram Bot

This is where you get the bot token — the password that lets your code control the bot.

1. Open Telegram on your phone or desktop
2. Search for **@BotFather** (it has a blue checkmark ✅)
3. Send it: `/newbot`
4. It will ask: **"What name do you want for your bot?"**
   - Type a display name, e.g. `Code Forwarder`
5. It will ask: **"Choose a username for your bot"**
   - Must end in `bot`, e.g. `my_codes_forwarder_bot`
   - If it's taken, try adding numbers: `my_codes_fw_1234_bot`
6. BotFather replies with your **bot token**. It looks like this:
   ```
   7123456789:AAF-xyz789abc123def456_something
   ```
7. **COPY THIS TOKEN** — you'll need it in Step 7

> ⚠️ **Never share this token publicly.** Anyone with it can control your bot.

---

### Step 5: Get Your Telegram User ID

The bot needs to know WHO to send codes to. Your User ID is a number, not your username.

1. Open Telegram
2. Search for **@userinfobot**
3. Send it any message (just say "hi")
4. It replies with something like:
   ```
   Id: 123456789
   First: John
   ```
5. **COPY YOUR ID NUMBER** — you'll need it in Step 7

---

### Step 6: Generate an iCloud App-Specific Password

> ⚠️ **You CANNOT use your normal Apple ID password.** iCloud requires a special app password for third-party apps connecting via IMAP. This is a security feature.

1. Open your browser and go to **[appleid.apple.com](https://appleid.apple.com)**
2. Sign in with your Apple ID
3. Go to **Sign-In & Security**
4. Click **App-Specific Passwords**
5. Click the **+** (plus) button
6. Name it something like `Code Forwarder`
7. Apple generates a password that looks like: `abcd-efgh-ijkl-mnop`
8. **COPY THIS PASSWORD IMMEDIATELY** — Apple only shows it once

> 💡 If you can't find "App-Specific Passwords", make sure you have **Two-Factor Authentication** enabled on your Apple ID. It's required.

---

### Step 7: Configure Your `.env` File

This is where ALL your secrets go. The bot reads this file on startup.

1. In the project folder, find the file called `.env.example`
2. **Copy it** and rename the copy to `.env`:
   ```bash
   cp .env.example .env
   ```
   On Windows:
   ```bash
   copy .env.example .env
   ```
3. Open `.env` in your text editor and fill in YOUR values:

```env
# ── Telegram ──────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN=7123456789:AAF-xyz789abc123def456_something
ALLOWED_USER_IDS=123456789
EMAIL_RECIPIENT_ID=123456789

# ── iCloud IMAP ───────────────────────────────────────────────────────────────
IMAP_HOST=imap.mail.me.com
IMAP_PORT=993
IMAP_USER=yourname@icloud.com
IMAP_PASS=abcd-efgh-ijkl-mnop

# ── Optional ──────────────────────────────────────────────────────────────────
EMAIL_POLL_INTERVAL=30
```

**What each field means:**

| Field | What to put | Example |
|-------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | The token from Step 4 (BotFather) | `7123456789:AAF-xyz...` |
| `ALLOWED_USER_IDS` | Your Telegram user ID from Step 5. Comma-separated if multiple people. | `123456789` or `123456789,987654321` |
| `EMAIL_RECIPIENT_ID` | Who receives the codes (usually same as your user ID) | `123456789` |
| `IMAP_HOST` | Leave as `imap.mail.me.com` | `imap.mail.me.com` |
| `IMAP_PORT` | Leave as `993` | `993` |
| `IMAP_USER` | Your iCloud email address | `john@icloud.com` |
| `IMAP_PASS` | The App-Specific Password from Step 6 | `abcd-efgh-ijkl-mnop` |
| `EMAIL_POLL_INTERVAL` | How often to check (in seconds). 30 is good. | `30` |

> ⚠️ The `.env` file is in `.gitignore` — it will NOT be uploaded to GitHub. Your secrets stay local.

---

### Step 8: Start the Bot

```bash
python3 bot.py
```

You should see:
```
2026-05-17 23:00:00 [INFO] 🚀 iCloud Code Forwarder Bot starting...
2026-05-17 23:00:01 [INFO] 📬 Email monitor started — polling every 30s
```

Now go to Telegram, find your bot (the username you created in Step 4), and send `/start`.

The bot should reply with its status.

**To test it:** send yourself a verification code from any service (e.g., log in to Twitter and trigger a code). The bot should forward it within 30 seconds.

---

### Step 9: Keep It Running 24/7 (Optional)

If you just close the terminal, the bot stops. Here's how to keep it running:

**Option A — On a VPS (DigitalOcean, etc.):**
```bash
# Install screen (run once)
sudo apt install screen

# Start a named screen session
screen -S codebot

# Run the bot
python3 bot.py

# Detach: press Ctrl+A, then D
# Reattach later: screen -r codebot
```

**Option B — Using systemd (Linux):**
```bash
sudo nano /etc/systemd/system/codeforwarder.service
```

Paste:
```ini
[Unit]
Description=iCloud Code Forwarder Bot
After=network.target

[Service]
Type=simple
User=YOUR_LINUX_USERNAME
WorkingDirectory=/path/to/forwarder
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable codeforwarder
sudo systemctl start codeforwarder

# Check status:
sudo systemctl status codeforwarder

# View logs:
journalctl -u codeforwarder -f
```

---

## Bot Commands

| Command | What it does |
|---------|-------------|
| `/start` | Shows bot status + help |
| `/last_codes` | Shows the last 10 codes received (since bot started) |
| `/status` | Shows IMAP connection details and stats |

---

## What a Code Notification Looks Like

When a verification email arrives, you get this in Telegram:

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

## Supported Services

The bot automatically recognises emails from these services with their icons:

| Service | Domains recognised |
|---------|-------------------|
| 🐦 Twitter / X | twitter.com, x.com, twimg.com |
| 🍎 Apple / iCloud | apple.com, icloud.com |
| 🔍 Google / Gmail | google.com, gmail.com |
| 📸 Instagram | instagram.com |
| 🔵 Facebook / Meta | facebookmail.com, meta.com |
| 🔞 OnlyFans | onlyfans.com |
| ✈️ Telegram | telegram.org |
| 👻 Snapchat | snapchat.com |
| 🎵 TikTok | tiktok.com |
| 🔴 Reddit | reddit.com |

Any other service falls back to showing the sender's domain (e.g. `📨 discord.com`).

---

## Project Files Explained

```
forwarder/
├── bot.py              # Main entry point — starts the Telegram bot + email polling
├── email_monitor.py    # IMAP connection, email parsing, code extraction logic
├── requirements.txt    # Python packages to install
├── .env.example        # Template for your config — copy to .env
├── .env                # YOUR config (not tracked by git)
└── .gitignore          # Tells git to ignore .env and cache files
```

---

## Troubleshooting

### "IMAP auth/connection error"
- Your `IMAP_PASS` is wrong. It must be an **App-Specific Password**, not your Apple ID password.
- Go back to Step 6 and generate a new one.

### "TELEGRAM_BOT_TOKEN is not set"
- You didn't create the `.env` file, or it's empty. Go back to Step 7.

### Bot runs but no codes arrive
- Make sure you have **unread** verification emails in your inbox. The bot only reads UNSEEN messages.
- Send yourself a test verification code (e.g., log in to Twitter).
- Check that `EMAIL_RECIPIENT_ID` in `.env` matches your Telegram user ID.

### "pip: command not found"
- Try `pip3` instead of `pip`.
- Or use: `python3 -m pip install -r requirements.txt`

### Multiple people need codes
- Add all their Telegram user IDs to `ALLOWED_USER_IDS`, separated by commas:
  ```
  ALLOWED_USER_IDS=111111111,222222222,333333333
  ```
- Set `EMAIL_RECIPIENT_ID` to whoever should receive the code notifications.

---

## Architecture (For Claude / Technical Reference)

If you're pasting this to Claude or another AI to help you modify the bot, here's how it works:

### `bot.py` — Telegram Bot + Scheduler
- Uses `python-telegram-bot` v21.6 (async)
- On startup (`post_init`), spawns an async background task `email_polling_loop`
- The loop calls `check_new_verification_emails()` in a thread executor every `POLL_SECS` seconds
- When codes are returned, it formats and sends them to `RECIPIENT_ID`
- Has 3 command handlers: `/start`, `/last_codes`, `/status`
- Authorization: only user IDs in `ALLOWED_USER_IDS` can interact with the bot

### `email_monitor.py` — IMAP Email Scanner
- Connects to iCloud IMAP over SSL (port 993)
- Searches for `UNSEEN` (unread) emails in INBOX
- For each email:
  1. Checks if it's a verification email using keyword matching (`_VERIF_KEYWORDS`)
  2. Extracts the code using regex patterns (`_CODE_PATTERNS`) — tries body first, then subject
  3. Identifies the service by sender domain (`_SERVICES` dict)
  4. Extracts the recipient alias (the Hide My Email address)
  5. Marks the email as `SEEN` so it won't be processed again
- Returns a list of dicts with: service, sender, to_alias, subject, code, received time
- Keeps last 30 codes in memory (`RECENT_CODES` deque)

### Key Design Decisions
- **No database** — codes are stored in memory only (deque with maxlen=30). Restarting the bot clears history.
- **No webhooks** — uses polling for both Telegram and IMAP. Simpler to deploy, no need for a public URL.
- **Thread executor for IMAP** — `imaplib` is synchronous/blocking, so it runs in a thread to not block the async Telegram bot.
- **Marks emails as read** — once processed, an email won't trigger again even if the bot restarts.

### Environment Variables
```
TELEGRAM_BOT_TOKEN    — Bot token from @BotFather
ALLOWED_USER_IDS      — Comma-separated Telegram user IDs allowed to use the bot
EMAIL_RECIPIENT_ID    — The Telegram user ID that receives code notifications
IMAP_HOST             — IMAP server (default: imap.mail.me.com)
IMAP_PORT             — IMAP port (default: 993)
IMAP_USER             — iCloud email address
IMAP_PASS             — App-Specific Password (NOT Apple ID password)
EMAIL_POLL_INTERVAL   — Seconds between inbox checks (default: 30)
```

### Requirements
- Python 3.9+
- `python-telegram-bot==21.6`
- `python-dotenv==1.0.1`
- Built-in: `imaplib`, `email`, `re`, `asyncio`
