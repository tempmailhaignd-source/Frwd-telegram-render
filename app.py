#!/usr/bin/env python3
# app.py - EXTREME DEBUG (Har message ka data dikhega)
# CAT Shadow Hacker

import os
import asyncio
import logging
import json
from pathlib import Path
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from telethon.tl.types import (
    MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage,
    MessageMediaPoll, MessageMediaContact, MessageMediaGeo,
    MessageMediaVenue, MessageMediaDice, MessageMediaGame,
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
DELAY = 1.5
PARALLEL = 1  # DEBUG ke liye

SESSION_STRING = "1BVtsOHoBu5FHvTd_gQBWx_41G-zbF_5Xc8iUCgphoZHz0PuzvL_HiS4mGJwK_8_QeUivqGJV7ghLyTNIW5FICnttX8aWdY8K3MF2NLza708E5SliPbWfZG3e0kMScesvRz8c1c2Mxl7JQDFY-baOFG5bF-zEU4PfaGOErtTdm-iMD_3LSwQbyqeP3HguPKy7WvtA-5F9Ycz82hM0kd2GsTdQfFD236D11einxiRIApq29qzVT8Lxiec3bKD9h2oyNhAGh4FcLwAGCVmnHmQ2WFMYgT97TGZAXSYncThQXhPibxv8p_eV1Go5WwFaHmaM9avj-BKBrp9qHhlvyBX0tAFTW6DgeG0="

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ EXTREME DEBUG"

@app.route('/health')
def health():
    return "OK"

# ============================================================
# DEBUG COPIER
# ============================================================

class ExtremeDebugCopier:
    def __init__(self):
        self.client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        self.source = SOURCE
        self.dest = DEST
        self.delay = DELAY
        self.parallel = PARALLEL
        
        self.copied = 0
        self.failed = []
        self.processed_ids = set()
        self.semaphore = asyncio.Semaphore(PARALLEL)
        
        self.download_folder = Path("downloads")
        self.download_folder.mkdir(exist_ok=True)
        
        self.progress_file = Path("progress_debug.json")
        self.load_progress()
    
    def load_progress(self):
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    self.copied = data.get('copied', 0)
                    self.processed_ids = set(data.get('processed_ids', []))
                    self.failed = data.get('failed', [])
                    logger.info(f"📌 Loaded: {self.copied} copied")
                    return
            except:
                pass
        logger.info("📌 Fresh start")
    
    def save_progress(self):
        try:
            data = {
                'copied': self.copied,
                'processed_ids': list(self.processed_ids),
                'failed': self.failed
            }
            with open(self.progress_file, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    async def copy_one(self, msg):
        async with self.semaphore:
            if msg.id in self.processed_ids:
                return True
            
            # 🔥 EXTREME DEBUG: Sab print karo
            logger.info("=" * 60)
            logger.info(f"📌 MESSAGE ID: {msg.id}")
            logger.info(f"📌 Has Media: {msg.media is not None}")
            
            if msg.media:
                logger.info(f"📌 Media Type: {type(msg.media).__name__}")
                
                if isinstance(msg.media, MessageMediaPhoto):
                    logger.info("📸 PHOTO DETECTED")
                    
                elif isinstance(msg.media, MessageMediaDocument):
                    doc = msg.media.document
                    if doc:
                        logger.info(f"📌 Document MIME: {doc.mime_type}")
                        logger.info(f"📌 Document Size: {doc.size} bytes")
                        
                        # Check all attributes
                        for attr in doc.attributes:
                            logger.info(f"📌 Attribute: {type(attr).__name__}")
                            if isinstance(attr, DocumentAttributeFilename):
                                logger.info(f"📌 FILENAME: {attr.file_name}")
                            elif isinstance(attr, DocumentAttributeVideo):
                                logger.info(f"📌 VIDEO: {attr.duration}s, {attr.w}x{attr.h}")
                            elif isinstance(attr, DocumentAttributeAudio):
                                logger.info(f"📌 AUDIO: {attr.duration}s")
                            elif isinstance(attr, DocumentAttributeSticker):
                                logger.info("📌 STICKER DETECTED")
                
                elif isinstance(msg.media, MessageMediaWebPage):
                    logger.info("🌐 WEB PAGE DETECTED")
                    if msg.media.webpage:
                        logger.info(f"📌 WebPage Title: {msg.media.webpage.title}")
                        logger.info(f"📌 WebPage URL: {msg.media.webpage.url}")
                
                elif isinstance(msg.media, MessageMediaPoll):
                    logger.info("📊 POLL DETECTED")
                
                elif isinstance(msg.media, MessageMediaContact):
                    logger.info("👤 CONTACT DETECTED")
                
                elif isinstance(msg.media, MessageMediaGeo):
                    logger.info("📍 LOCATION DETECTED")
                
                elif isinstance(msg.media, MessageMediaVenue):
                    logger.info("📍 VENUE DETECTED")
                
                elif isinstance(msg.media, MessageMediaDice):
                    logger.info("🎲 DICE DETECTED")
                
                elif isinstance(msg.media, MessageMediaGame):
                    logger.info("🎮 GAME DETECTED")
                
                else:
                    logger.info(f"⚠️ UNKNOWN MEDIA: {type(msg.media).__name__}")
            
            if msg.text:
                logger.info(f"📌 Caption/Text: {msg.text[:200]}...")
            
            # Now try to copy
            try:
                # --- PHOTO ---
                if isinstance(msg.media, MessageMediaPhoto):
                    logger.info("📥 Downloading PHOTO...")
                    path = await self.client.download_media(msg, file=str(self.download_folder / f"photo_{msg.id}.jpg"))
                    if path and os.path.exists(path):
                        logger.info(f"✅ Downloaded: {path} ({os.path.getsize(path)} bytes)")
                        await self.client.send_file(self.dest, path, caption=msg.text or "")
                        os.remove(path)
                        self.copied += 1
                        self.processed_ids.add(msg.id)
                        self.save_progress()
                        logger.info(f"✅ {self.copied}: {msg.id} (Photo)")
                    else:
                        logger.error(f"❌ PHOTO DOWNLOAD FAILED: {msg.id}")
                    return True
                
                # --- VIDEO / DOCUMENT / AUDIO / STICKER ---
                if isinstance(msg.media, MessageMediaDocument):
                    doc = msg.media.document
                    if not doc:
                        logger.warning(f"⚠️ No document data: {msg.id}")
                        return True
                    
                    # Get filename
                    filename = None
                    for attr in doc.attributes:
                        if isinstance(attr, DocumentAttributeFilename):
                            filename = attr.file_name
                            break
                    
                    if not filename:
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
                    
                    logger.info(f"📥 Downloading: {filename}")
                    path = await self.client.download_media(msg, file=str(self.download_folder / filename))
                    
                    if path and os.path.exists(path):
                        logger.info(f"✅ Downloaded: {path} ({os.path.getsize(path)} bytes)")
                        
                        # Detect if it's video
                        is_video = False
                        is_audio = False
                        for attr in doc.attributes:
                            if isinstance(attr, DocumentAttributeVideo):
                                is_video = True
                            elif isinstance(attr, DocumentAttributeAudio):
                                is_audio = True
                        
                        await self.client.send_file(
                            self.dest,
                            path,
                            caption=msg.text or "",
                            supports_streaming=True,
                            force_document=False
                        )
                        os.remove(path)
                        self.copied += 1
                        self.processed_ids.add(msg.id)
                        self.save_progress()
                        logger.info(f"✅ {self.copied}: {msg.id} ({filename})")
                    else:
                        logger.error(f"❌ DOWNLOAD FAILED: {msg.id}")
                    return True
                
                # --- WEB PAGE ---
                if isinstance(msg.media, MessageMediaWebPage):
                    webpage = msg.media.webpage
                    if webpage:
                        text = f"🔗 {webpage.title or 'Link'}\n{webpage.description or ''}\n{webpage.url or ''}"
                    else:
                        text = msg.text or "🔗 Web Page"
                    await self.client.send_message(self.dest, text)
                    self.copied += 1
                    self.processed_ids.add(msg.id)
                    self.save_progress()
                    logger.info(f"✅ {self.copied}: {msg.id} (Web Page)")
                    return True
                
                # --- POLL ---
                if isinstance(msg.media, MessageMediaPoll):
                    poll = msg.media.poll
                    answers = "\n".join([f"• {a.text}" for a in poll.answers])
                    text = f"📊 POLL\nQuestion: {poll.question}\n\n{answers}"
                    await self.client.send_message(self.dest, text)
                    self.copied += 1
                    self.processed_ids.add(msg.id)
                    self.save_progress()
                    logger.info(f"✅ {self.copied}: {msg.id} (Poll)")
                    return True
                
                # --- CONTACT ---
                if isinstance(msg.media, MessageMediaContact):
                    contact = msg.media
                    text = f"👤 CONTACT\nName: {contact.first_name} {contact.last_name or ''}\nPhone: {contact.phone_number}"
                    await self.client.send_message(self.dest, text)
                    self.copied += 1
                    self.processed_ids.add(msg.id)
                    self.save_progress()
                    logger.info(f"✅ {self.copied}: {msg.id} (Contact)")
                    return True
                
                # --- LOCATION ---
                if isinstance(msg.media, MessageMediaGeo):
                    geo = msg.media
                    text = f"📍 Location\nLat: {geo.lat}, Lon: {geo.long}"
                    await self.client.send_message(self.dest, text)
                    self.copied += 1
                    self.processed_ids.add(msg.id)
                    self.save_progress()
                    logger.info(f"✅ {self.copied}: {msg.id} (Location)")
                    return True
                
                # --- VENUE ---
                if isinstance(msg.media, MessageMediaVenue):
                    geo = msg.media
                    text = f"📍 {geo.title}\n{geo.address}\nLat: {geo.geo.lat}, Lon: {geo.geo.long}"
                    await self.client.send_message(self.dest, text)
                    self.copied += 1
                    self.processed_ids.add(msg.id)
                    self.save_progress()
                    logger.info(f"✅ {self.copied}: {msg.id} (Venue)")
                    return True
                
                # --- GAME ---
                if isinstance(msg.media, MessageMediaGame):
                    game = msg.media.game
                    text = f"🎮 GAME\n{game.title}\n{game.description}"
                    await self.client.send_message(self.dest, text)
                    self.copied += 1
                    self.processed_ids.add(msg.id)
                    self.save_progress()
                    logger.info(f"✅ {self.copied}: {msg.id} (Game)")
                    return True
                
                # --- DICE ---
                if isinstance(msg.media, MessageMediaDice):
                    dice = msg.media
                    emojis = {1: "🎲", 2: "🎯", 3: "🏀", 4: "⚽", 5: "🎳"}
                    text = f"{emojis.get(dice.emoticon, '🎲')} Dice: {dice.value}"
                    await self.client.send_message(self.dest, text)
                    self.copied += 1
                    self.processed_ids.add(msg.id)
                    self.save_progress()
                    logger.info(f"✅ {self.copied}: {msg.id} (Dice)")
                    return True
                
                # --- TEXT (No media) ---
                if not msg.media:
                    await self.client.send_message(self.dest, msg.text or "")
                    self.copied += 1
                    self.processed_ids.add(msg.id)
                    self.save_progress()
                    logger.info(f"✅ {self.copied}: {msg.id} (Text)")
                    return True
                
                # --- UNKNOWN ---
                logger.warning(f"⚠️ UNKNOWN: {msg.id}")
                self.copied += 1
                self.processed_ids.add(msg.id)
                self.save_progress()
                return True
                
            except FloodWaitError as e:
                logger.warning(f"⏳ Flood {e.seconds}s")
                await asyncio.sleep(e.seconds + 5)
            except Exception as e:
                logger.error(f"❌ {msg.id}: {e}")
                import traceback
                traceback.print_exc()
            
            return False
    
    async def run(self):
        await self.client.start()
        
        logger.info("=" * 60)
        logger.info("🔍 EXTREME DEBUG - Har message ka data print hoga")
        logger.info("=" * 60)
        
        offset = 0
        batch_num = 0
        
        while True:
            try:
                messages = await self.client.get_messages(
                    self.source,
                    limit=20,  # Sirf 20 messages debug ke liye
                    offset_id=offset,
                    reverse=True
                )
                
                if not messages:
                    logger.info("✅ Done!")
                    break
                
                batch_num += 1
                logger.info(f"📦 Batch {batch_num}: {len(messages)} messages")
                
                for msg in messages:
                    if msg.id in self.processed_ids:
                        continue
                    await self.copy_one(msg)
                    await asyncio.sleep(self.delay)
                
                if messages:
                    offset = messages[-1].id
                
            except Exception as e:
                logger.error(f"❌ Batch: {e}")
                await asyncio.sleep(5)
        
        logger.info("=" * 60)
        logger.info(f"✅ Copied: {self.copied}")
        logger.info(f"⚠️ Failed: {len(self.failed)}")
        logger.info("=" * 60)

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import threading
    
    logger.info("🔑 Starting EXTREME DEBUG...")
    
    copier = ExtremeDebugCopier()
    
    def start_bot():
        asyncio.run(copier.run())
    
    thread = threading.Thread(target=start_bot, daemon=True)
    thread.start()
    logger.info("🚀 EXTREME DEBUG running")
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
