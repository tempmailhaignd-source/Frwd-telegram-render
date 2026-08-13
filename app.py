#!/usr/bin/env python3
# app.py - Private Group Copier (Python 3.14 Compatible)
# CAT Shadow Hacker

import os
import asyncio
import threading
import logging
from pathlib import Path
from flask import Flask
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import (
    MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage,
    MessageMediaPoll, MessageMediaContact, MessageMediaGeo,
    MessageMediaVenue, MessageMediaDice, MessageMediaGame,
    DocumentAttributeVideo, DocumentAttributeAudio,
    DocumentAttributeFilename, DocumentAttributeSticker
)

# ============================================================
# CONFIGURATION
# ============================================================

API_ID = int(os.environ.get("API_ID", 30622410))
API_HASH = os.environ.get("API_HASH", "ac0e642a6cf43ced04f3cc2eabf5a21d")
SOURCE_CHAT = int(os.environ.get("SOURCE_CHAT", -1003801298314))
DEST_CHAT = int(os.environ.get("DEST_CHAT", -1003882932953))
DELAY = float(os.environ.get("DELAY", 1.5))

# ============================================================
# SETUP LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running!"

@app.route('/health')
def health():
    return "OK"

# ============================================================
# FORWARDER CLASS
# ============================================================

class Forwarder:
    def __init__(self):
        self.client = TelegramClient("render_session", API_ID, API_HASH)
        self.source = SOURCE_CHAT
        self.dest = DEST_CHAT
        self.delay = DELAY
        self.copied = 0
        self.skipped = 0
        self.errors = 0
        self.progress_file = Path("progress.txt")
        self.last_id = self.load_progress()
        self.download_folder = Path("downloads")
        self.download_folder.mkdir(exist_ok=True)
    
    def load_progress(self):
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return int(f.read().strip())
            except:
                return 0
        return 0
    
    def save_progress(self, msg_id):
        with open(self.progress_file, 'w') as f:
            f.write(str(msg_id))
    
    async def download_media_with_retry(self, msg, max_retries=3):
        for attempt in range(max_retries):
            try:
                path = await self.client.download_media(
                    msg,
                    file=str(self.download_folder / f"msg_{msg.id}_{int(os.times().user)}.tmp")
                )
                if path and os.path.exists(path) and os.path.getsize(path) > 0:
                    return path
                elif path:
                    try:
                        os.remove(path)
                    except:
                        pass
            except Exception as e:
                logger.warning(f"Download attempt {attempt+1} failed: {e}")
                await asyncio.sleep(2)
        return None
    
    def get_caption(self, msg):
        if msg.text:
            return msg.text
        if msg.media and hasattr(msg.media, 'caption'):
            return msg.media.caption
        return ""
    
    async def copy_message(self, msg):
        try:
            # --- TEXT ---
            if not msg.media:
                await self.client.send_message(
                    self.dest,
                    msg.text or "",
                    parse_mode='html' if msg.text and ('<b>' in msg.text or '<i>' in msg.text) else None,
                    reply_to=msg.reply_to_msg_id if msg.is_reply else None
                )
                self.copied += 1
                self.last_id = msg.id
                self.save_progress(msg.id)
                logger.info(f"✅ {self.copied}: {msg.id} (Text)")
                return True
            
            # --- POLL ---
            if isinstance(msg.media, MessageMediaPoll):
                poll = msg.media.poll
                answers = "\n".join([f"• {a.text}" for a in poll.answers])
                text = f"📊 POLL\nQuestion: {poll.question}\n\n{answers}"
                await self.client.send_message(self.dest, text)
                self.copied += 1
                self.last_id = msg.id
                self.save_progress(msg.id)
                logger.info(f"✅ {self.copied}: {msg.id} (Poll)")
                return True
            
            # --- CONTACT ---
            if isinstance(msg.media, MessageMediaContact):
                contact = msg.media
                text = f"👤 CONTACT\nName: {contact.first_name} {contact.last_name or ''}\nPhone: {contact.phone_number}"
                await self.client.send_message(self.dest, text)
                self.copied += 1
                self.last_id = msg.id
                self.save_progress(msg.id)
                logger.info(f"✅ {self.copied}: {msg.id} (Contact)")
                return True
            
            # --- LOCATION ---
            if isinstance(msg.media, MessageMediaGeo) or isinstance(msg.media, MessageMediaVenue):
                geo = msg.media
                if isinstance(geo, MessageMediaVenue):
                    text = f"📍 {geo.title}\n{geo.address}\nLat: {geo.geo.lat}, Lon: {geo.geo.long}"
                else:
                    text = f"📍 Location\nLat: {geo.lat}, Lon: {geo.long}"
                await self.client.send_message(self.dest, text)
                self.copied += 1
                self.last_id = msg.id
                self.save_progress(msg.id)
                logger.info(f"✅ {self.copied}: {msg.id} (Location)")
                return True
            
            # --- GAME ---
            if isinstance(msg.media, MessageMediaGame):
                game = msg.media.game
                text = f"🎮 GAME\n{game.title}\n{game.description}"
                await self.client.send_message(self.dest, text)
                self.copied += 1
                self.last_id = msg.id
                self.save_progress(msg.id)
                logger.info(f"✅ {self.copied}: {msg.id} (Game)")
                return True
            
            # --- DICE ---
            if isinstance(msg.media, MessageMediaDice):
                dice = msg.media
                emojis = {1: "🎲", 2: "🎯", 3: "🏀", 4: "⚽", 5: "🎳"}
                text = f"{emojis.get(dice.emoticon, '🎲')} Dice: {dice.value}"
                await self.client.send_message(self.dest, text)
                self.copied += 1
                self.last_id = msg.id
                self.save_progress(msg.id)
                logger.info(f"✅ {self.copied}: {msg.id} (Dice)")
                return True
            
            # --- MEDIA (Photo, Video, Document, Voice, Sticker) ---
            if msg.media:
                logger.info(f"📥 Downloading media: {msg.id}")
                path = await self.download_media_with_retry(msg)
                
                if path and os.path.exists(path):
                    logger.info(f"📤 Uploading: {msg.id}")
                    caption = self.get_caption(msg)
                    if len(caption) > 1000:
                        caption = caption[:997] + "..."
                    
                    await self.client.send_file(
                        self.dest,
                        path,
                        caption=caption,
                        supports_streaming=True,
                        force_document=False,
                        reply_to=msg.reply_to_msg_id if msg.is_reply else None
                    )
                    
                    try:
                        os.remove(path)
                    except:
                        pass
                    
                    self.copied += 1
                    self.last_id = msg.id
                    self.save_progress(msg.id)
                    logger.info(f"✅ {self.copied}: {msg.id} (Media)")
                    return True
                else:
                    logger.warning(f"⚠️ Download failed: {msg.id}")
                    self.skipped += 1
                    return False
            
            self.skipped += 1
            return False
            
        except FloodWaitError as e:
            logger.warning(f"⏳ Flood wait {e.seconds}s")
            await asyncio.sleep(e.seconds + 2)
            return False
        except Exception as e:
            logger.error(f"❌ {msg.id}: {e}")
            self.errors += 1
            return False
    
    async def run(self):
        await self.client.start()
        
        logger.info("=" * 60)
        logger.info(f"📤 Source: {self.source}")
        logger.info(f"📥 Destination: {self.dest}")
        logger.info(f"📌 Resuming from: {self.last_id}")
        logger.info("=" * 60)
        
        offset = self.last_id
        
        while True:
            try:
                messages = await self.client.get_messages(
                    self.source,
                    limit=100,
                    offset_id=offset,
                    reverse=True
                )
                
                if not messages:
                    logger.info("⏳ No new messages. Waiting...")
                    await asyncio.sleep(60)
                    continue
                
                logger.info(f"📦 {len(messages)} messages fetched")
                
                for msg in messages:
                    if msg.id <= self.last_id:
                        continue
                    await self.copy_message(msg)
                    await asyncio.sleep(self.delay)
                
                if messages:
                    offset = messages[-1].id
                
            except FloodWaitError as e:
                logger.warning(f"⏳ Flood wait: {e.seconds}s")
                await asyncio.sleep(e.seconds + 5)
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                await asyncio.sleep(10)

# ============================================================
# MAIN
# ============================================================

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    forwarder = Forwarder()
    loop.run_until_complete(forwarder.run())

if __name__ == "__main__":
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    logger.info("🚀 Bot started in background")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
