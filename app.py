#!/usr/bin/env python3
# app.py - Complete Private Group Copier (All Media + Filenames)
# CAT Shadow Hacker - 100% Working on Render

import os
import asyncio
import logging
from pathlib import Path
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from telethon.tl.types import (
    MessageMediaPhoto, MessageMediaDocument,
    DocumentAttributeFilename, DocumentAttributeVideo,
    DocumentAttributeAudio, DocumentAttributeSticker
)

# ============================================================
# CONFIG
# ============================================================

API_ID = 30622410
API_HASH = "ac0e642a6cf43ced04f3cc2eabf5a21d"
SOURCE = -1003801298314
DEST = -1003882932953
DELAY = 2.5

# 🔑 Session String
SESSION_STRING = "1BVtsOHoBu5FHvTd_gQBWx_41G-zbF_5Xc8iUCgphoZHz0PuzvL_HiS4mGJwK_8_QeUivqGJV7ghLyTNIW5FICnttX8aWdY8K3MF2NLza708E5SliPbWfZG3e0kMScesvRz8c1c2Mxl7JQDFY-baOFG5bF-zEU4PfaGOErtTdm-iMD_3LSwQbyqeP3HguPKy7WvtA-5F9Ycz82hM0kd2GsTdQfFD236D11einxiRIApq29qzVT8Lxiec3bKD9h2oyNhAGh4FcLwAGCVmnHmQ2WFMYgT97TGZAXSYncThQXhPibxv8p_eV1Go5WwFaHmaM9avj-BKBrp9qHhlvyBX0tAFTW6DgeG0="

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# FLASK APP (Render Health Check)
# ============================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running! (All Media + Filenames)"

@app.route('/health')
def health():
    return "OK"

# ============================================================
# MAIN COPIER
# ============================================================

async def run_copier():
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
            
            logger.info(f"📦 Processing {len(messages)} messages...")
            
            for msg in messages:
                try:
                    # --- TEXT MESSAGE ---
                    if not msg.media:
                        await client.send_message(DEST, msg.text or "")
                        copied += 1
                        logger.info(f"✅ {copied}: {msg.id} (Text)")
                        await asyncio.sleep(DELAY)
                        continue
                    
                    # --- PHOTO ---
                    if isinstance(msg.media, MessageMediaPhoto):
                        logger.info(f"📸 Downloading photo: {msg.id}")
                        path = await client.download_media(msg, file=str(download_folder / f"photo_{msg.id}.jpg"))
                        if path and os.path.exists(path):
                            caption = msg.text or ""
                            await client.send_file(DEST, path, caption=caption)
                            os.remove(path)
                            copied += 1
                            logger.info(f"✅ {copied}: {msg.id} (Photo)")
                        else:
                            logger.warning(f"⚠️ Photo download failed: {msg.id}")
                        await asyncio.sleep(DELAY)
                        continue
                    
                    # --- DOCUMENT / VIDEO / AUDIO / STICKER ---
                    if isinstance(msg.media, MessageMediaDocument):
                        doc = msg.media.document
                        if not doc:
                            continue
                        
                        # Get filename
                        filename = None
                        for attr in doc.attributes:
                            if isinstance(attr, DocumentAttributeFilename):
                                filename = attr.file_name
                                break
                        
                        if not filename:
                            # Generate filename based on type
                            if doc.mime_type:
                                ext = doc.mime_type.split('/')[-1]
                                if 'video' in doc.mime_type:
                                    filename = f"video_{msg.id}.{ext}"
                                elif 'audio' in doc.mime_type:
                                    filename = f"audio_{msg.id}.{ext}"
                                elif 'image' in doc.mime_type:
                                    filename = f"image_{msg.id}.{ext}"
                                else:
                                    filename = f"file_{msg.id}.{ext}"
                            else:
                                filename = f"file_{msg.id}.bin"
                        
                        logger.info(f"📥 Downloading: {filename} ({msg.id})")
                        path = await client.download_media(msg, file=str(download_folder / filename))
                        
                        if path and os.path.exists(path):
                            caption = msg.text or ""
                            await client.send_file(
                                DEST,
                                path,
                                caption=caption,
                                supports_streaming=True,
                                force_document=False
                            )
                            os.remove(path)
                            copied += 1
                            logger.info(f"✅ {copied}: {msg.id} ({filename})")
                        else:
                            logger.warning(f"⚠️ Download failed: {msg.id} ({filename})")
                        await asyncio.sleep(DELAY)
                        continue
                    
                    # --- OTHER MEDIA (Fallback) ---
                    if msg.media:
                        logger.info(f"📥 Downloading media: {msg.id}")
                        path = await client.download_media(msg, file=str(download_folder / f"media_{msg.id}.bin"))
                        if path and os.path.exists(path):
                            caption = msg.text or ""
                            await client.send_file(DEST, path, caption=caption)
                            os.remove(path)
                            copied += 1
                            logger.info(f"✅ {copied}: {msg.id} (Media)")
                        else:
                            logger.warning(f"⚠️ Media download failed: {msg.id}")
                        await asyncio.sleep(DELAY)
                        continue
                    
                except FloodWaitError as e:
                    logger.warning(f"⏳ Flood wait {e.seconds}s")
                    await asyncio.sleep(e.seconds + 5)
                except Exception as e:
                    logger.error(f"❌ {msg.id}: {e}")
            
            if messages:
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
    
    def start_bot():
        asyncio.run(run_copier())
    
    thread = threading.Thread(target=start_bot, daemon=True)
    thread.start()
    logger.info("🚀 Bot started in background")
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
