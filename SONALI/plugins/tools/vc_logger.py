# SONALI/plugins/tools/vc_logger.py

from pyrogram import Client, filters
from pyrogram.types import ChatMemberUpdated, Message
from logging import getLogger, basicConfig
from config import STRING_SESSION  # Using your string session from config.py

# Configure logger
basicConfig(level=20)
logger = getLogger(__name__)

# Track active VC users and current songs
vc_users = {}
current_song = {}
# Enabled chats for logging
enabled_chats = set()

# Initialize assistant client
app = Client(STRING_SESSION)

# ================== VC LOGGING ==================
@app.on_chat_member_updated(filters.group)
async def vc_members_logger(client: Client, chat_member_updated: ChatMemberUpdated):
    chat_id = chat_member_updated.chat.id
    if chat_id not in enabled_chats:
        return

    user = chat_member_updated.new_chat_member.user
    old_status = chat_member_updated.old_chat_member.status
    new_status = chat_member_updated.new_chat_member.status

    if old_status in ["left", "kicked"] and new_status in ["member", "administrator"]:
        vc_users[user.id] = True
        logger.info(f"{user.first_name} joined VC in {chat_member_updated.chat.title}")
        await client.send_message(chat_id, f"✅ {user.first_name} joined the VC!")

    elif old_status in ["member", "administrator"] and new_status in ["left", "kicked"]:
        vc_users.pop(user.id, None)
        logger.info(f"{user.first_name} left VC in {chat_member_updated.chat.title}")
        await client.send_message(chat_id, f"❌ {user.first_name} left the VC!")

@app.on_message(filters.group & filters.text)
async def vc_message_logger(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id not in enabled_chats:
        return

    if message.from_user and message.from_user.id in vc_users:
        logger.info(f"[VC Message] {message.from_user.first_name}: {message.text}")

# ================== MUSIC LOGGING ==================
async def log_music(chat_id: int, song_name: str):
    if chat_id not in enabled_chats:
        return
    current_song[chat_id] = song_name
    logger.info(f"[Music] Now playing in {chat_id}: {song_name}")
    await app.send_message(chat_id, f"🎵 Now playing: **{song_name}**")

async def music_stopped(chat_id: int):
    if chat_id not in enabled_chats:
        return
    song = current_song.pop(chat_id, None)
    if song:
        logger.info(f"[Music] Stopped in {chat_id}: {song}")
        await app.send_message(chat_id, f"⏹ Music stopped: **{song}**")

async def music_skipped(chat_id: int, next_song: str):
    if chat_id not in enabled_chats:
        return
    old_song = current_song.get(chat_id, None)
    current_song[chat_id] = next_song
    if old_song:
        logger.info(f"[Music] Skipped {old_song} -> {next_song} in {chat_id}")
        await app.send_message(chat_id, f"⏭ Skipped **{old_song}**, now playing **{next_song}**")

# ================== ENABLE / DISABLE COMMAND ==================
@app.on_message(filters.command("vclog") & filters.group)
async def toggle_vclog(client: Client, message: Message):
    if not message.from_user or not message.from_user.id:
        return

    chat_id = message.chat.id
    if len(message.command) < 2:
        await message.reply("Usage: /vclog on | off")
        return

    option = message.command[1].lower()
    if option == "on":
        enabled_chats.add(chat_id)
        await message.reply("✅ VC + Music logging ENABLED in this chat.")
    elif option == "off":
        enabled_chats.discard(chat_id)
        await message.reply("❌ VC + Music logging DISABLED in this chat.")
    else:
        await message.reply("Usage: /vclog on | off")
