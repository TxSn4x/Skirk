
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from MukeshRobot import dispatcher
from MukeshRobot.modules.disable import DisableAbleCommandHandler

# In-memory toggle storage
VC_LOGGER_ENABLED = set()

# ───────────── ENABLE / DISABLE ───────────── #

def vc_logger_toggle(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if not args:
        enabled = "enabled" if chat_id in VC_LOGGER_ENABLED else "disabled"
        update.effective_message.reply_text(f"VC Logger is currently: {enabled}")
        return

    cmd = args[0].lower()
    if cmd == "enable":
        VC_LOGGER_ENABLED.add(chat_id)
        update.effective_message.reply_text("✅ VC Logger enabled for this chat.")
    elif cmd == "disable":
        VC_LOGGER_ENABLED.discard(chat_id)
        update.effective_message.reply_text("❌ VC Logger disabled for this chat.")
    else:
        update.effective_message.reply_text("Usage: /vclogger enable|disable")

# ───────────── HANDLER FOR ASSISTANT BOT ───────────── #

def vc_logger_notify(chat_id, text, context: CallbackContext):
    if chat_id in VC_LOGGER_ENABLED:
        msg = context.bot.send_message(chat_id=chat_id, text=text)
        # Auto-delete after 30 seconds
        asyncio.get_event_loop().create_task(auto_delete(msg))

async def auto_delete(msg):
    await asyncio.sleep(30)
    try:
        await msg.delete()
    except:
        pass

# ───────────── REGISTER ───────────── #

dispatcher.add_handler(
    DisableAbleCommandHandler("vclogger", vc_logger_toggle, pass_args=True)
)

__mod_name__ = "VC Logger"
__command_list__ = ["vclogger"]
