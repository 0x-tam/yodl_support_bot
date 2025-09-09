import os, html, textwrap
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ["BOT_TOKEN"]
SUPPORT_GROUP_ID = int(os.environ["SUPPORT_GROUP_ID"])

def who(update: Update) -> str:
    u = update.effective_user
    name = u.first_name or "User"
    return f"{name} (@{u.username})" if u.username else name

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message(
        "Hi! You’ve reached support. Please tell us what’s wrong."
    )

async def user_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat

    # Auto reply to the user
    await msg.reply_text(
        "✅ Thank you for reaching out to us.\n"
        "Our support team has received your message and is reviewing it.\n"
        "We’ll get back to you as soon as possible — usually within 24 hours."
    )

    # Forward to support group
    header = textwrap.dedent(f"""
    ✉️ From {who(update)}
    chat_id: <code>{chat.id}</code>
    """).strip()
    body = html.escape(msg.text) if msg.text else "(non-text)"
    await context.bot.send_message(
        chat_id=SUPPORT_GROUP_ID,
        text=header + "\n\n" + body,
        parse_mode=ParseMode.HTML,
    )

async def cmd_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != SUPPORT_GROUP_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /to <chat_id> <message>")
        return
    try:
        target = int(context.args[0])
    except ValueError:
        await update.message.reply_text("chat_id must be an integer.")
        return
    text = " ".join(context.args[1:])
    await context.bot.send_message(chat_id=target, text=text)
    await update.message.reply_text("✅ Sent.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, user_msg))
    app.add_handler(CommandHandler("to", cmd_to))
    app.run_polling()

if __name__ == "__main__":
    main()
