import time
import asyncio
from pyrogram import filters
from pyrogram.errors import ChannelInvalid
from pyrogram.enums import ChatType, ChatMembersFilter
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from py_yt import VideosSearch

import config
from SONALI import app
from SONALI.misc import _boot_
from SONALI.plugins.sudo.sudoers import sudoers_list
from SONALI.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
    connect_to_chat,
)
from SONALI.utils.decorators.language import LanguageStart
from SONALI.utils.formatters import get_readable_time
from SONALI.utils.inline import start_panel
from config import BANNED_USERS
from strings import get_string


# ─────────────────────────────────────────
# START (NO HELP, REDIRECT ONLY)
# ─────────────────────────────────────────
@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    # Plain "/start" → do nothing (silent redirect)
    if len(message.text.split()) == 1:
        return

    name = message.text.split(None, 1)[1]

    # /start connect_xxx
    if name.startswith("connect_"):
        chat_id = name[8:]
        try:
            title = (await app.get_chat(chat_id)).title
        except ChannelInvalid:
            return await message.reply_text(
                f"ʟᴏᴏʟ ʟɪᴋᴇ ɪ ᴀᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ ɪᴅ {chat_id}"
            )

        admin_ids = [
            member.user.id
            async for member in app.get_chat_members(
                chat_id, filter=ChatMembersFilter.ADMINISTRATORS
            )
        ]

        if message.from_user.id not in admin_ids:
            return await message.reply_text(
                f"sᴏʀʀʏ sɪʀ, ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ᴏғ {title}"
            )

        a = await connect_to_chat(message.from_user.id, chat_id)
        return await message.reply_text(
            f"ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ {title}" if a else a
        )

    # /start sud
    if name.startswith("sud"):
        return await sudoers_list(client=client, message=message, _=_)

    # /start inf_xxx
    if name.startswith("inf"):
        m = await message.reply_text("🔎")
        query = name.replace("info_", "", 1)
        query = f"https://www.youtube.com/watch?v={query}"

        results = VideosSearch(query, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration = result["duration"]
            views = result["viewCount"]["short"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            channellink = result["channel"]["link"]
            channel = result["channel"]["name"]
            link = result["link"]
            published = result["publishedTime"]

        await m.delete()

        return await app.send_photo(
            message.chat.id,
            photo=thumbnail,
            caption=_["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            ),
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(text=_["S_B_8"], url=link),
                    InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                ]]
            ),
        )


# ─────────────────────────────────────────
# GROUP /START → IGNORE
# ─────────────────────────────────────────
@app.on_message(filters.command(["start"]) & filters.group)
async def start_gp(_, message: Message):
    return


# ─────────────────────────────────────────
# WELCOME HANDLER (UNCHANGED)
# ─────────────────────────────────────────
@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                await message.chat.ban_member(member.id)

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                await message.reply_photo(
                    config.START_IMG_URL,
                    caption=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(start_panel(_)),
                )

                await add_served_chat(message.chat.id)
                await message.stop_propagation()

        except Exception as e:
            print(e)
