#!/usr/bin/env python3
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ---------------- CONFIG ----------------
BOT_TOKEN = "7947639550:AAHEtB3KRztXvgDfXM-r3-mWRCA8Vn-G5_g"
BACKUP_CHANNEL = "@gdndndm"
MAIN_CHANNEL = -1002877068674
# ----------------------------------------

logging.basicConfig(level=logging.INFO)

# /start 1-100
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /start <from>-<to>\nExample: /start 1-100")
        return

    try:
        # parse range
        msg_range = context.args[0].split("-")
        start_id = int(msg_range[0])
        end_id = int(msg_range[1])

        await update.message.reply_text(f"📤 Copying messages {start_id} to {end_id}...")

        # loop through given IDs
        for msg_id in range(start_id, end_id + 1):
            try:
                await context.bot.copy_message(
                    chat_id=MAIN_CHANNEL,      # target channel
                    from_chat_id=BACKUP_CHANNEL,  # source channel
                    message_id=msg_id
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Error copying {msg_id}: {e}")

        await update.message.reply_text("✅ Done!")

    except Exception as e:
        await update.message.reply_text(f"Invalid format ❌\nError: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
