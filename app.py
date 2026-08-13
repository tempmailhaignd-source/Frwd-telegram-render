#!/usr/bin/env python3
# app.py - Private Group Copier with Session String
# CAT Shadow Hacker - 100% Working on Render

import os
import asyncio
import logging
from pathlib import Path
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

# ============================================================
# CONFIG
# ============================================================

API_ID = 30622410
API_HASH = "ac0e642a6cf43ced04f3cc2eabf5a21d"
SOURCE = -1003801298314
DEST = -1003882932953
DELAY = 2.5

# 🔑 Session String (Render Environment Variable se load)
SESSION_STRING = "1BVtsOHoBu5FHvTd_gQBWx_41G-zbF_5Xc8iUCgphoZHz0PuzvL_HiS4mGJwK_8_QeUivqGJV7ghLyTNIW5FICnttX8aWdY8K3MF2NLza708E5SliPbWfZG3e0kMScesvRz8c1c2Mxl7JQDFY-baOFG5bF-zEU4PfaGOErtTdm-iMD_3LSwQbyqeP3HguPKy7WvtA-5F9Ycz82hM0kd2GsTdQfFD236D11einxiRIApq29qzVT8Lxiec3bKD9h2oyNhAGh4FcLwAGCVmnHmQ2WFMYgT97TGZAXSYncThQXhPibxv8p_eV1Go5WwFaHmaM9avj-BKBrp9qHhlvyBX0tAFTW6DgeG0="

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# FLASK APP (Render Health Check)
# ============================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running! (Session String Mode)"

@app.route('/health')
def health():
    return "OK"

# ============================================================
# MAIN COPIER
# ============================================================

async def run_copier():
    # 🔑 Session String se client initialize
    logger.info("🔑 Initializing with Session String...")
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    
    logger.info(f"📤 Source: {SOURCE}")
    logger.info(f"📥 Destination: {DEST}")
    logger.info(f"⏱️ Delay: {DELAY}s")
    
    offset = 0
    copied = 0
    download_folder = Path("downloads")
    download_folder.mkdir(exist_ok=True)
    
    while True:
        try:
            messages = await client.get_messages(SOURCE, limit=50, offset_id=offset, reverse=True)
            if not messages:
                logger.info("⏳ No new messages. Waiting...")
                await asyncio.sleep(60)
                continue
            
            for msg in messages:
                try:
                    if msg.media:
                        # Download and send
                        path = await client.download_media(msg, file=str(download_folder / f"{msg.id}.tmp"))
                        if path and os.path.exists(path):
                            await client.send_file(DEST, path, caption=msg.text or "", supports_streaming=True)
                            os.remove(path)
                        else:
                            logger.warning(f"⚠️ Download failed: {msg.id}")
                            continue
                    else:
                        # Just text
                        await client.send_message(DEST, msg.text or "")
                    
                    copied += 1
                    logger.info(f"✅ {copied}: {msg.id}")
                    await asyncio.sleep(DELAY)
                    
                except FloodWaitError as e:
                    logger.warning(f"⏳ Flood wait {e.seconds}s")
                    await asyncio.sleep(e.seconds + 5)
                except Exception as e:
                    logger.error(f"❌ {msg.id}: {e}")
            
            offset = messages[-1].id
            
        except Exception as e:
            logger.error(f"❌ Batch error: {e}")
            await asyncio.sleep(10)

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import threading
    
    logger.info("🔑 Session String loaded successfully!")
    logger.info("🚀 Bot will start without phone/OTP")
    
    # Bot ko background thread mein chalao
    def start_bot():
        asyncio.run(run_copier())
    
    thread = threading.Thread(target=start_bot, daemon=True)
    thread.start()
    logger.info("🚀 Bot started in background")
    
    # Flask server (Render health check ke liye)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
