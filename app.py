#!/usr/bin/env python3
# app.py - Fast + Safe Zero Miss Copier
# CAT Shadow Hacker - 60k in 2-3 Days, Account Safe

import os
import asyncio
import logging
import json
from pathlib import Path
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, RPCError
from telethon.tl.types import (
    MessageMediaPhoto, MessageMediaDocument,
    DocumentAttributeFilename, DocumentAttributeVideo,
    DocumentAttributeAudio, DocumentAttributeSticker
)

# ============================================================
# CONFIG — FAST + SAFE
# ============================================================

API_ID = 30622410
API_HASH = "ac0e642a6cf43ced04f3cc2eabf5a21d"
SOURCE = -1003801298314
DEST = -1003882932953

# 🚀 SPEED SETTINGS (Safe for account)
DELAY = 1.2                    # 1.2 sec between messages
PARALLEL = 2                   # 2 messages at a time
MAX_RETRIES = 3                # Retry on failure
BATCH_SIZE = 150               # More messages per fetch

# 🔑 Session String
SESSION_STRING = "1BVtsOHoBu5FHvTd_gQBWx_41G-zbF_5Xc8iUCgphoZHz0PuzvL_HiS4mGJwK_8_QeUivqGJV7ghLyTNIW5FICnttX8aWdY8K3MF2NLza708E5SliPbWfZG3e0kMScesvRz8c1c2Mxl7JQDFY-baOFG5bF-zEU4PfaGOErtTdm-iMD_3LSwQbyqeP3HguPKy7WvtA-5F9Ycz82hM0kd2GsTdQfFD236D11einxiRIApq29qzVT8Lxiec3bKD9h2oyNhAGh4FcLwAGCVmnHmQ2WFMYgT97TGZAXSYncThQXhPibxv8p_eV1Go5WwFaHmaM9avj-BKBrp9qHhlvyBX0tAFTW6DgeG0="

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot running! (Fast + Safe)"

@app.route('/health')
def health():
    return "OK"

# ============================================================
# FAST + SAFE COPIER
# ============================================================

class FastSafeCopier:
    def __init__(self):
        self.client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        self.source = SOURCE
        self.dest = DEST
        self.delay = DELAY
        self.parallel = PARALLEL
        self.max_retries = MAX_RETRIES
        self.batch_size = BATCH_SIZE
        
        self.copied = 0
        self.failed = []
        self.processed_ids = set()
        self.semaphore = asyncio.Semaphore(PARALLEL)
        
        self.download_folder = Path("downloads")
        self.download_folder.mkdir(exist_ok=True)
        
        self.progress_file = Path("progress_fast.json")
        self.load_progress()
    
    def load_progress(self):
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    self.copied = data.get('copied', 0)
                    self.processed_ids = set(data.get('processed_ids', []))
                    self.failed = data.get('failed', [])
                    logger.info(f"📌 Loaded: {self.copied} copied, {len(self.processed_ids)} processed")
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
            except:
                await asyncio.sleep(2)
        return None
    
    async def copy_one(self, msg):
        """Copy single message with parallel safe"""
        async with self.semaphore:
            if msg.id in self.processed_ids:
                return True
            
            for attempt in range(self.max_retries):
                try:
                    # --- TEXT ---
                    if not msg.media:
                        await self.client.send_message(self.dest, msg.text or "")
                        self.copied += 1
                        self.processed_ids.add(msg.id)
                        self.save_progress()
                        logger.info(f"✅ {self.copied}: {msg.id} (Text)")
                        return True
                    
                    # --- PHOTO ---
                    if isinstance(msg.media, MessageMediaPhoto):
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
                    
                    # --- DOCUMENT/VIDEO/AUDIO ---
                    if isinstance(msg.media, MessageMediaDocument):
                        doc = msg.media.document
                        if not doc:
                            self.copied += 1
                            self.processed_ids.add(msg.id)
                            self.save_progress()
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
                                else:
                                    filename = f"file_{msg.id}.{ext}"
                            else:
                                filename = f"file_{msg.id}.bin"
                        
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
                            logger.info(f"✅ {self.copied}: {msg.id} ({filename})")
                            return True
                        continue
                    
                    # --- OTHER MEDIA ---
                    if msg.media:
                        path = await self.download_with_retry(msg)
                        if path:
                            await self.client.send_file(self.dest, path, caption=msg.text or "")
                            os.remove(path)
                            self.copied += 1
                            self.processed_ids.add(msg.id)
                            self.save_progress()
                            logger.info(f"✅ {self.copied}: {msg.id} (Media)")
                            return True
                        continue
                    
                    # Unknown type — mark as processed
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
            
            # All retries failed
            self.failed.append(msg.id)
            self.save_progress()
            logger.error(f"❌ {msg.id}: All {self.max_retries} attempts failed!")
            return False
    
    async def run(self):
        await self.client.start()
        
        logger.info("=" * 60)
        logger.info(f"📤 Source: {self.source}")
        logger.info(f"📥 Destination: {self.dest}")
        logger.info(f"⚡ Parallel: {self.parallel}")
        logger.info(f"⏱️ Delay: {self.delay}s")
        logger.info(f"📦 Batch: {self.batch_size}")
        logger.info("=" * 60)
        
        # Get total count
        try:
            total = await self.client.get_messages(self.source, limit=0)
            total_count = total.total if hasattr(total, 'total') else 0
            logger.info(f"📊 Total: ~{total_count}")
        except:
            pass
        
        offset = 0
        batch_num = 0
        
        while True:
            try:
                messages = await self.client.get_messages(
                    self.source,
                    limit=self.batch_size,
                    offset_id=offset,
                    reverse=True
                )
                
                if not messages:
                    logger.info("✅ All messages fetched!")
                    break
                
                batch_num += 1
                logger.info(f"📦 Batch {batch_num}: {len(messages)} messages")
                
                # Parallel processing
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
                
                # Small break between batches
                await asyncio.sleep(0.5)
                
            except FloodWaitError as e:
                logger.warning(f"⏳ Flood: {e.seconds}s")
                await asyncio.sleep(e.seconds + 5)
            except Exception as e:
                logger.error(f"❌ Batch: {e}")
                await asyncio.sleep(10)
        
        # Retry failed
        if self.failed:
            logger.info(f"🔄 Retrying {len(self.failed)} failed messages...")
            for msg_id in self.failed[:]:
                try:
                    msg = await self.client.get_messages(self.source, ids=msg_id)
                    if msg:
                        await self.copy_one(msg)
                except:
                    pass
        
        logger.info("=" * 60)
        logger.info(f"✅ Total copied: {self.copied}")
        logger.info(f"⚠️ Failed: {len(self.failed)}")
        logger.info("=" * 60)

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import threading
    
    logger.info("🔑 Starting Fast + Safe Copier")
    
    copier = FastSafeCopier()
    
    def start_bot():
        asyncio.run(copier.run())
    
    thread = threading.Thread(target=start_bot, daemon=True)
    thread.start()
    logger.info("🚀 Bot running (Fast + Safe)")
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
