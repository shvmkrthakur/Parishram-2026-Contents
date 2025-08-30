#!/usr/bin/env python3
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ---------------- CONFIG ----------------
BOT_TOKEN = "7947639550:AAHEtB3KRztXvgDfXM-r3-mWRCA8Vn-G5_g"
BACKUP_CHANNEL = "@gdndndm"      # source channel username OR id
MAIN_CHANNEL   = -1002371985459  # target channel id
REMOVE_TEXT    = "✨ Powered By : @ParishramZone"
# ----------------------------------------

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /start <from>-<to>\nExample: /start 1-100")
        return

    try:
        msg_range = context.args[0].split("-")
        start_id = int(msg_range[0])
        end_id = int(msg_range[1]) if len(msg_range) > 1 else start_id

        await update.message.reply_text(f"📤 Copying messages {start_id} to {end_id}...")

        for msg_id in range(start_id, end_id + 1):
            try:
                # fetch the original message
                msg = await context.bot.forward_message(
                    chat_id=update.effective_chat.id,   # temp forward to user (self)
                    from_chat_id=BACKUP_CHANNEL,
                    message_id=msg_id
                )
                await msg.delete()  # delete temp forward

                # now fetch real message
                original = await context.bot.get_chat(BACKUP_CHANNEL)
            except Exception as e:
                await update.message.reply_text(f"❌ Error fetching {msg_id}: {e}")
                continue

            try:
                # check message type and resend clean
                if msg.text:
                    cleaned_text = msg.text.replace(REMOVE_TEXT, "").strip()
                    await context.bot.send_message(MAIN_CHANNEL, cleaned_text)

                elif msg.caption:
                    cleaned_caption = msg.caption.replace(REMOVE_TEXT, "").strip()
                    if msg.photo:
                        await context.bot.send_photo(MAIN_CHANNEL, photo=msg.photo[-1].file_id, caption=cleaned_caption)
                    elif msg.video:
                        await context.bot.send_video(MAIN_CHANNEL, video=msg.video.file_id, caption=cleaned_caption)
                    elif msg.document:
                        await context.bot.send_document(MAIN_CHANNEL, document=msg.document.file_id, caption=cleaned_caption)
                    else:
                        await context.bot.send_message(MAIN_CHANNEL, cleaned_caption)

                else:
                    # fallback just copy
                    await context.bot.copy_message(MAIN_CHANNEL, BACKUP_CHANNEL, msg_id)

            except Exception as e:
                await update.message.reply_text(f"❌ Error sending {msg_id}: {e}")

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
