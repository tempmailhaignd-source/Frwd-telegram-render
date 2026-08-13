#!/usr/bin/env python3
# app.py - Complete Private Group Copier (All Media Types)
# CAT Shadow Hacker - 100% Working

import os
import asyncio
import threading
import logging
import shutil
from pathlib import Path
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from telethon.tl.types import (
    MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage,
    MessageMediaPoll, MessageMediaContact, MessageMediaGeo,
    MessageMediaVenue, MessageMediaDice, MessageMediaGame,
    DocumentAttributeVideo, DocumentAttributeAudio,
    DocumentAttributeFilename, DocumentAttributeSticker,
    MessageMediaAudio, MessageMediaVoice
)

# ============================================================
# CONFIGURATION
# ============================================================

API_ID = int(os.environ.get("API_ID", 30622410))
API_HASH = os.environ.get("API_HASH", "ac0e642a6cf43ced04f3cc2eabf5a21d")
SOURCE_CHAT = int(os.environ.get("SOURCE_CHAT", -1003801298314))
DEST_CHAT = int(os.environ.get("DEST_CHAT", -1003882932953))
DELAY = float(os.environ.get("DELAY", 1.5))

# 🔑 Session String
SESSION_STRING = "1BVtsOHoBu5FHvTd_gQBWx_41G-zbF_5Xc8iUCgphoZHz0PuzvL_HiS4mGJwK_8_QeUivqGJV7ghLyTNIW5FICnttX8aWdY8K3MF2NLza708E5SliPbWfZG3e0kMScesvRz8c1c2Mxl7JQDFY-baOFG5bF-zEU4PfaGOErtTdm-iMD_3LSwQbyqeP3HguPKy7WvtA-5F9Ycz82hM0kd2GsTdQfFD236D11einxiRIApq29qzVT8Lxiec3bKD9h2oyNhAGh4FcLwAGCVmnHmQ2WFMYgT97TGZAXSYncThQXhPibxv8p_eV1Go5WwFaHmaM9avj-BKBrp9qHhlvyBX0tAFTW6DgeG0="

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
    return "✅ Bot is running! (All Media Types)"

@app.route('/health')
def health():
    return "OK"

# ============================================================
# FORWARDER CLASS - COMPLETE
# ============================================================

class Forwarder:
    def __init__(self):
        logger.info("🔑 Initializing with Session String...")
        self.client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
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
        """Download media with retry logic"""
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
        """Extract caption/text from message"""
        if msg.text:
            return msg.text
        if hasattr(msg, 'message') and msg.message:
            return msg.message
        if msg.media and hasattr(msg.media, 'caption'):
            return msg.media.caption
        return ""
    
    def get_file_name(self, msg):
        """Extract filename from media"""
        if not msg.media or not isinstance(msg.media, MessageMediaDocument):
            return None
        doc = msg.media.document
        if doc:
            for attr in doc.attributes:
                if isinstance(attr, DocumentAttributeFilename):
                    return attr.file_name
        return None
    
    async def copy_media_group(self, messages):
        """Copy album/media group together"""
        try:
            # Group messages by media group ID
            groups = {}
            for msg in messages:
                if msg.grouped_id:
                    if msg.grouped_id not in groups:
                        groups[msg.grouped_id] = []
                    groups[msg.grouped_id].append(msg)
                else:
                    # Single media
                    await self.copy_message(msg)
            
            # Process each group
            for group_id, group_msgs in groups.items():
                try:
                    # Download all media in group
                    media_files = []
                    for msg in group_msgs:
                        path = await self.download_media_with_retry(msg)
                        if path:
                            media_files.append(path)
                    
                    if media_files:
                        # Send as album
                        caption = self.get_caption(group_msgs[0])
                        await self.client.send_file(
                            self.dest,
                            media_files,
                            caption=caption,
                            supports_streaming=True,
                            force_document=False
                        )
                        
                        # Clean up
                        for path in media_files:
                            try:
                                os.remove(path)
                            except:
                                pass
                        
                        # Update progress for all messages in group
                        for msg in group_msgs:
                            self.copied += 1
                            self.last_id = msg.id
                            self.save_progress(msg.id)
                            logger.info(f"✅ {self.copied}: {msg.id} (Media Group)")
                except Exception as e:
                    logger.error(f"❌ Group {group_id} failed: {e}")
        except Exception as e:
            logger.error(f"❌ Media group processing error: {e}")
    
    async def copy_message(self, msg):
        """Copy a single message - ALL TYPES"""
        try:
            # --- 1. TEXT MESSAGE ---
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
            
            # --- 2. POLL ---
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
            
            # --- 3. CONTACT ---
            if isinstance(msg.media, MessageMediaContact):
                contact = msg.media
                text = f"👤 CONTACT\nName: {contact.first_name} {contact.last_name or ''}\nPhone: {contact.phone_number}"
                await self.client.send_message(self.dest, text)
                self.copied += 1
                self.last_id = msg.id
                self.save_progress(msg.id)
                logger.info(f"✅ {self.copied}: {msg.id} (Contact)")
                return True
            
            # --- 4. LOCATION / VENUE ---
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
            
            # --- 5. GAME ---
            if isinstance(msg.media, MessageMediaGame):
                game = msg.media.game
                text = f"🎮 GAME\n{game.title}\n{game.description}"
                await self.client.send_message(self.dest, text)
                self.copied += 1
                self.last_id = msg.id
                self.save_progress(msg.id)
                logger.info(f"✅ {self.copied}: {msg.id} (Game)")
                return True
            
            # --- 6. DICE ---
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
            
            # --- 7. WEB PAGE / PREVIEW ---
            if isinstance(msg.media, MessageMediaWebPage):
                webpage = msg.media.webpage
                if webpage:
                    text = f"🔗 {webpage.title or 'Link'}\n{webpage.description or ''}\n{webpage.url or ''}"
                    await self.client.send_message(self.dest, text)
                    self.copied += 1
                    self.last_id = msg.id
                    self.save_progress(msg.id)
                    logger.info(f"✅ {self.copied}: {msg.id} (Web Page)")
                    return True
            
            # --- 8. MEDIA (Photo, Video, Document, Voice, Sticker, Audio) ---
            if msg.media:
                # Check if it's a sticker
                is_sticker = False
                is_voice = False
                is_audio = False
                is_video = False
                mime_type = None
                
                if isinstance(msg.media, MessageMediaDocument):
                    doc = msg.media.document
                    if doc:
                        for attr in doc.attributes:
                            if isinstance(attr, DocumentAttributeSticker):
                                is_sticker = True
                            elif isinstance(attr, DocumentAttributeAudio):
                                is_audio = True
                            elif isinstance(attr, DocumentAttributeVideo):
                                is_video = True
                        if doc.mime_type:
                            mime_type = doc.mime_type
                            if 'voice' in mime_type:
                                is_voice = True
                
                logger.info(f"📥 Downloading media: {msg.id}")
                path = await self.download_media_with_retry(msg)
                
                if path and os.path.exists(path):
                    logger.info(f"📤 Uploading: {msg.id}")
                    caption = self.get_caption(msg)
                    if len(caption) > 1000:
                        caption = caption[:997] + "..."
                    
                    # Send based on media type
                    await self.client.send_file(
                        self.dest,
                        path,
                        caption=caption,
                        supports_streaming=True,
                        force_document=is_sticker,  # Stickers as document
                        voice_note=is_voice,
                        video_note=is_video,
                        reply_to=msg.reply_to_msg_id if msg.is_reply else None
                    )
                    
                    try:
                        os.remove(path)
                    except:
                        pass
                    
                    self.copied += 1
                    self.last_id = msg.id
                    self.save_progress(msg.id)
                    media_type = "Sticker" if is_sticker else "Voice" if is_voice else "Audio" if is_audio else "Video" if is_video else "Media"
                    logger.info(f"✅ {self.copied}: {msg.id} ({media_type})")
                    return True
                else:
                    logger.warning(f"⚠️ Download failed: {msg.id}")
                    self.skipped += 1
                    return False
            
            # --- 9. UNKNOWN ---
            logger.warning(f"⚠️ Unknown message type: {msg.id} ({type(msg.media)})")
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
        """Main loop"""
        logger.info("🔑 Authenticating with Session String...")
        await self.client.start()
        
        logger.info("=" * 60)
        logger.info(f"📤 Source: {self.source}")
        logger.info(f"📥 Destination: {self.dest}")
        logger.info(f"📌 Resuming from: {self.last_id}")
        logger.info("=" * 60)
        
        offset = self.last_id
        
        while True:
            try:
                # Fetch messages
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
                
                # Process messages
                i = 0
                while i < len(messages):
                    msg = messages[i]
                    
                    if msg.id <= self.last_id:
                        i += 1
                        continue
                    
                    # Check for media group
                    if msg.grouped_id:
                        # Collect all messages in group
                        group_msgs = []
                        while i < len(messages) and messages[i].grouped_id == msg.grouped_id:
                            if messages[i].id > self.last_id:
                                group_msgs.append(messages[i])
                            i += 1
                        
                        if group_msgs:
                            await self.copy_media_group(group_msgs)
                    else:
                        # Single message
                        await self.copy_message(msg)
                        i += 1
                    
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
    logger.info("🔑 Session String loaded successfully!")
    logger.info("🚀 Bot will start without phone/OTP")
    
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    logger.info("🚀 Bot started in background (All Media Types)")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
