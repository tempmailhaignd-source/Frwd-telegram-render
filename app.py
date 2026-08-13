#!/usr/bin/env python3
# SIMPLE_COPIER.py - No frills, just works

import os
import asyncio
import logging
from pathlib import Path
from telethon import TelegramClient
from telethon.errors import FloodWaitError

# ============================================================
# CONFIG
# ============================================================

API_ID = 30622410
API_HASH = "ac0e642a6cf43ced04f3cc2eabf5a21d"
SOURCE = -1003801298314
DEST = -1003882932953
DELAY = 2.5

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# MAIN
# ============================================================

async def main():
    client = TelegramClient("simple_session", API_ID, API_HASH)
    await client.start()
    
    logger.info(f"Source: {SOURCE}")
    logger.info(f"Destination: {DEST}")
    
    offset = 0
    copied = 0
    
    while True:
        try:
            messages = await client.get_messages(SOURCE, limit=50, offset_id=offset, reverse=True)
            if not messages:
                break
            
            for msg in messages:
                try:
                    if msg.media:
                        # Download and send
                        path = await client.download_media(msg, file="downloads/")
                        if path:
                            await client.send_file(DEST, path, caption=msg.text or "")
                            os.remove(path)
                    else:
                        # Just text
                        await client.send_message(DEST, msg.text or "")
                    
                    copied += 1
                    logger.info(f"✅ {copied}: {msg.id}")
                    await asyncio.sleep(DELAY)
                    
                except FloodWaitError as e:
                    logger.warning(f"⏳ Waiting {e.seconds}s")
                    await asyncio.sleep(e.seconds + 5)
                except Exception as e:
                    logger.error(f"❌ {msg.id}: {e}")
            
            offset = messages[-1].id
            
        except Exception as e:
            logger.error(f"Batch error: {e}")
            await asyncio.sleep(10)
    
    logger.info(f"✅ Done! Copied {copied} messages")

if __name__ == "__main__":
    Path("downloads").mkdir(exist_ok=True)
    asyncio.run(main())
