import os, html, textwrap
from telegram import Update, Message
from telegram.constants import ParseMode
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

BOT_TOKEN = os.environ["BOT_TOKEN"]
# Put 0 first, deploy, run /gid in your support group to get the real ID, then update and redeploy.
FORWARD_TO_ID = int(os.environ.get("FORWARD_TO_ID", "0"))

def who(update: Update) -> str:
    u = update.effective_user
    name = u.first_name or "User"
    return f"{name} (@{u.username})" if u.username else name

# /gid helper to discover a group's numeric chat id
async def gid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Group ID: {update.effective_chat.id}")

# Forward every message the bot receives to FORWARD_TO_ID
async def any_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg: Message = update.effective_message

    # Do nothing until FORWARD_TO_ID is configured
    if FORWARD_TO_ID == 0:
        return

    # Avoid loops: ignore messages originating in the destination chat
    if chat.id == FORWARD_TO_ID:
        return

    # Build a small header with sender info
    header = textwrap.dedent(f"""
    ✉️ From {who(update)}
    chat_id: <code>{chat.id}</code>
    """).strip()

    # Try to copy original message (keeps media); fall back to text if needed
    try:
        await msg.copy(
            chat_id=FORWARD_TO_ID,
            caption=(header if not msg.caption else f"{header}\n\n{msg.caption}"),
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        body = msg.text_html if msg.text else "(non-text message)"
        await context.bot.send_message(
            chat_id=FORWARD_TO_ID,
            text=header + "\n\n" + body,
            parse_mode=ParseMode.HTML,
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    # Command to get a chat's ID (send /gid in your support group)
    app.add_handler(CommandHandler("gid", gid_cmd))
    # Catch ALL messages (private, groups, media, etc.)
    app.add_handler(MessageHandler(filters.ALL, any_msg))
    app.run_polling()

if __name__ == "__main__":
    main()
