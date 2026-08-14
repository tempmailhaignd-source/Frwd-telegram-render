#!/usr/bin/env python3
# app.py - FINAL FIXED (Sab aayega - Video, Photo, Document, Web Page)
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
    DocumentAttributeAudio, DocumentAttributeSticker,
    WebPageEmpty
)

# ============================================================
# CONFIG
# ============================================================

API_ID = 30622410
API_HASH = "ac0e642a6cf43ced04f3cc2eabf5a21d"
SOURCE = -1003801298314
DEST = -1003882932953
DELAY = 1.5
PARALLEL = 2
MAX_RETRIES = 3

SESSION_STRING = "1BVtsOHoBu5FHvTd_gQBWx_41G-zbF_5Xc8iUCgphoZHz0PuzvL_HiS4mGJwK_8_QeUivqGJV7ghLyTNIW5FICnttX8aWdY8K3MF2NLza708E5SliPbWfZG3e0kMScesvRz8c1c2Mxl7JQDFY-baOFG5bF-zEU4PfaGOErtTdm-iMD_3LSwQbyqeP3HguPKy7WvtA-5F9Ycz82hM0kd2GsTdQfFD236D11einxiRIApq29qzVT8Lxiec3bKD9h2oyNhAGh4FcLwAGCVmnHmQ2WFMYgT97TGZAXSYncThQXhPibxv8p_eV1Go5WwFaHmaM9avj-BKBrp9qHhlvyBX0tAFTW6DgeG0="

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ FINAL FIXED - Sab aayega"

@app.route('/health')
def health():
    return "OK"

# ============================================================
# FINAL COPIER
# ============================================================

class FinalCopier:
    def __init__(self):
        self.client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        self.source = SOURCE
        self.dest = DEST
        self.delay = DELAY
        self.parallel = PARALLEL
        self.max_retries = MAX_RETRIES
        
        self.copied = 0
        self.failed = []
        self.processed_ids = set()
        self.semaphore = asyncio.Semaphore(PARALLEL)
        
        self.download_folder = Path("downloads")
        self.download_folder.mkdir(exist_ok=True)
        
        self.progress_file = Path("progress_final.json")
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
    
    def get_message_type(self, msg):
        if not msg.media:
            return "Text"
        
        media = msg.media
        
        if isinstance(media, MessageMediaPhoto):
            return "Photo"
        
        if isinstance(media, MessageMediaDocument):
            doc = media.document
            if doc:
                for attr in doc.attributes:
                    if isinstance(attr, DocumentAttributeSticker):
                        return "Sticker"
                    elif isinstance(attr, DocumentAttributeVideo):
                        return "Video"
                    elif isinstance(attr, DocumentAttributeAudio):
                        return "Audio"
                
                if doc.mime_type:
                    if 'video' in doc.mime_type:
                        return "Video"
                    elif 'audio' in doc.mime_type:
                        return "Audio"
                    elif 'image' in doc.mime_type:
                        return "Image"
                    else:
                        return "Document"
                return "Document"
            return "Document"
        
        if isinstance(media, MessageMediaWebPage):
            return "WebPage"
        if isinstance(media, MessageMediaPoll):
            return "Poll"
        if isinstance(media, MessageMediaContact):
            return "Contact"
        if isinstance(media, MessageMediaGeo):
            return "Location"
        if isinstance(media, MessageMediaVenue):
            return "Venue"
        if isinstance(media, MessageMediaDice):
            return "Dice"
        if isinstance(media, MessageMediaGame):
            return "Game"
        
        return f"Unknown"
    
    def get_filename(self, msg):
        if not msg.media or not isinstance(msg.media, MessageMediaDocument):
            return None
        doc = msg.media.document
        if not doc:
            return None
        for attr in doc.attributes:
            if isinstance(attr, DocumentAttributeFilename):
                return attr.file_name
        return None
    
    async def download_with_retry(self, msg, retries=3):
        for attempt in range(retries):
            try:
                path = await self.client.download_media(
                    msg,
                    file=str(self.download_folder / f"{msg.id}_{attempt}.tmp")
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
    
    async def copy_one(self, msg):
        async with self.semaphore:
            if msg.id in self.processed_ids:
                return True
            
            msg_type = self.get_message_type(msg)
            logger.info(f"🔍 {msg.id}: {msg_type}")
            
            for attempt in range(self.max_retries):
                try:
                    # --- TEXT ---
                    if msg_type == "Text":
                        await self.client.send_message(self.dest, msg.text or "")
                        self.copied += 1
                        self.processed_ids.add(msg.id)
                        self.save_progress()
                        logger.info(f"✅ {self.copied}: {msg.id} (Text)")
                        return True
                    
                    # --- PHOTO ---
                    if msg_type == "Photo":
                        path = await self.download_with_retry(msg)
                        if path:
                            await self.client.send_file(self.dest, path, caption=msg.text or "")
                            os.remove(path)
                            self.copied += 1
                            self.processed_ids.add(msg.id)
                            self.save_progress()
                            logger.info(f"✅ {self.copied}: {msg.id} (Photo)")
                            return True
                        continue
                    
                    # --- VIDEO ---
                    if msg_type == "Video":
                        filename = self.get_filename(msg) or f"video_{msg.id}.mp4"
                        path = await self.download_with_retry(msg)
                        if path:
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
                            logger.info(f"✅ {self.copied}: {msg.id} (Video: {filename})")
                            return True
                        continue
                    
                    # --- AUDIO / VOICE ---
                    if msg_type == "Audio":
                        filename = self.get_filename(msg) or f"audio_{msg.id}.mp3"
                        path = await self.download_with_retry(msg)
                        if path:
                            await self.client.send_file(
                                self.dest,
                                path,
                                caption=msg.text or "",
                                voice_note=True if msg.media.document and msg.media.document.mime_type and 'voice' in msg.media.document.mime_type else False
                            )
                            os.remove(path)
                            self.copied += 1
                            self.processed_ids.add(msg.id)
                            self.save_progress()
                            logger.info(f"✅ {self.copied}: {msg.id} (Audio: {filename})")
                            return True
                        continue
                    
                    # --- STICKER ---
                    if msg_type == "Sticker":
                        path = await self.download_with_retry(msg)
                        if path:
                            await self.client.send_file(self.dest, path, force_document=False)
                            os.remove(path)
                            self.copied += 1
                            self.processed_ids.add(msg.id)
                            self.save_progress()
                            logger.info(f"✅ {self.copied}: {msg.id} (Sticker)")
                            return True
                        continue
                    
                    # --- DOCUMENT / IMAGE ---
                    if msg_type in ["Document", "Image"]:
                        filename = self.get_filename(msg) or f"file_{msg.id}.bin"
                        path = await self.download_with_retry(msg)
                        if path:
                            await self.client.send_file(
                                self.dest,
                                path,
                                caption=msg.text or "",
                                force_document=True
                            )
                            os.remove(path)
                            self.copied += 1
                            self.processed_ids.add(msg.id)
                            self.save_progress()
                            logger.info(f"✅ {self.copied}: {msg.id} ({msg_type}: {filename})")
                            return True
                        continue
                    
                    # --- WEB PAGE (FIXED) ---
                    if msg_type == "WebPage":
                        webpage = msg.media.webpage
                        if webpage and not isinstance(webpage, WebPageEmpty):
                            title = getattr(webpage, 'title', 'Link')
                            description = getattr(webpage, 'description', '')
                            url = getattr(webpage, 'url', '')
                            text = f"🔗 {title}\n{description}\n{url}"
                        else:
                            # Fallback: send URL from message text
                            text = msg.text or "🔗 Web Page (link only)"
                        await self.client.send_message(self.dest, text)
                        self.copied += 1
                        self.processed_ids.add(msg.id)
                        self.save_progress()
                        logger.info(f"✅ {self.copied}: {msg.id} (Web Page)")
                        return True
                    
                    # --- POLL ---
                    if msg_type == "Poll":
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
                    if msg_type == "Contact":
                        contact = msg.media
                        text = f"👤 CONTACT\nName: {contact.first_name} {contact.last_name or ''}\nPhone: {contact.phone_number}"
                        await self.client.send_message(self.dest, text)
                        self.copied += 1
                        self.processed_ids.add(msg.id)
                        self.save_progress()
                        logger.info(f"✅ {self.copied}: {msg.id} (Contact)")
                        return True
                    
                    # --- LOCATION / VENUE ---
                    if msg_type in ["Location", "Venue"]:
                        geo = msg.media
                        if msg_type == "Venue":
                            text = f"📍 {geo.title}\n{geo.address}\nLat: {geo.geo.lat}, Lon: {geo.geo.long}"
                        else:
                            text = f"📍 Location\nLat: {geo.lat}, Lon: {geo.long}"
                        await self.client.send_message(self.dest, text)
                        self.copied += 1
                        self.processed_ids.add(msg.id)
                        self.save_progress()
                        logger.info(f"✅ {self.copied}: {msg.id} ({msg_type})")
                        return True
                    
                    # --- GAME ---
                    if msg_type == "Game":
                        game = msg.media.game
                        text = f"🎮 GAME\n{game.title}\n{game.description}"
                        await self.client.send_message(self.dest, text)
                        self.copied += 1
                        self.processed_ids.add(msg.id)
                        self.save_progress()
                        logger.info(f"✅ {self.copied}: {msg.id} (Game)")
                        return True
                    
                    # --- DICE ---
                    if msg_type == "Dice":
                        dice = msg.media
                        emojis = {1: "🎲", 2: "🎯", 3: "🏀", 4: "⚽", 5: "🎳"}
                        text = f"{emojis.get(dice.emoticon, '🎲')} Dice: {dice.value}"
                        await self.client.send_message(self.dest, text)
                        self.copied += 1
                        self.processed_ids.add(msg.id)
                        self.save_progress()
                        logger.info(f"✅ {self.copied}: {msg.id} (Dice)")
                        return True
                    
                    # --- UNKNOWN ---
                    logger.warning(f"⚠️ Unknown: {msg.id} ({msg_type})")
                    self.copied += 1
                    self.processed_ids.add(msg.id)
                    self.save_progress()
                    return True
                    
                except FloodWaitError as e:
                    logger.warning(f"⏳ Flood {e.seconds}s")
                    await asyncio.sleep(e.seconds + 5)
                except Exception as e:
                    logger.error(f"❌ {msg.id} attempt {attempt+1}: {e}")
                    await asyncio.sleep(2)
            
            self.failed.append(msg.id)
            self.save_progress()
            logger.error(f"❌ {msg.id}: All attempts failed!")
            return False
    
    async def run(self):
        await self.client.start()
        
        logger.info("=" * 60)
        logger.info("📤 Source: {}".format(self.source))
        logger.info("📥 Destination: {}".format(self.dest))
        logger.info("=" * 60)
        
        offset = 0
        batch_num = 0
        
        while True:
            try:
                messages = await self.client.get_messages(
                    self.source,
                    limit=100,
                    offset_id=offset,
                    reverse=True
                )
                
                if not messages:
                    logger.info("✅ All messages fetched!")
                    break
                
                batch_num += 1
                logger.info(f"📦 Batch {batch_num}: {len(messages)} messages")
                
                tasks = []
                for msg in messages:
                    if msg.id in self.processed_ids:
                        continue
                    tasks.append(self.copy_one(msg))
                
                if tasks:
                    await asyncio.gather(*tasks)
                
                if messages:
                    offset = messages[-1].id
                    logger.info(f"📌 Offset: {offset} | Copied: {self.copied}")
                
                await asyncio.sleep(0.5)
                
            except FloodWaitError as e:
                logger.warning(f"⏳ Flood: {e.seconds}s")
                await asyncio.sleep(e.seconds + 5)
            except Exception as e:
                logger.error(f"❌ Batch: {e}")
                await asyncio.sleep(10)
        
        if self.failed:
            logger.info(f"🔄 Retrying {len(self.failed)} failed...")
            for msg_id in self.failed[:]:
                try:
                    msg = await self.client.get_messages(self.source, ids=msg_id)
                    if msg:
                        await self.copy_one(msg)
                except:
                    pass
        
        logger.info("=" * 60)
        logger.info(f"✅ Copied: {self.copied}")
        logger.info(f"⚠️ Failed: {len(self.failed)}")
        if self.failed:
            logger.info(f"❌ Failed IDs: {self.failed}")
        logger.info("=" * 60)

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import threading
    
    logger.info("🔑 Starting FINAL COPIER...")
    
    copier = FinalCopier()
    
    def start_bot():
        asyncio.run(copier.run())
    
    thread = threading.Thread(target=start_bot, daemon=True)
    thread.start()
    logger.info("🚀 FINAL FIXED - Sab aayega!")
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
