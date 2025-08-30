#!/usr/bin/env python3
import logging, re
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ---------------- CONFIG ----------------
BOT_TOKEN = "7947639550:AAHEtB3KRztXvgDfXM-r3-mWRCA8Vn-G5_g"
BACKUP_CHANNEL = "@gdndndm"      # source channel username OR id
MAIN_CHANNEL   = -1002371985459  # target channel id
REMOVE_TEXT    = "✨ Powered By : @ParishramZone"
# ----------------------------------------

logging.basicConfig(level=logging.INFO)

def clean_text_keep_links(text: str, remove_text: str):
    """Remove unwanted text + formatting, keep only raw links."""
    if not text:
        return text
    # remove unwanted promo line
    text = text.replace(remove_text, "").strip()
    # regex: extract links
    links = re.findall(r'(https?://\S+|t\.me/\S+)', text)
    # remove all formatting chars (Telegram entities won’t be used)
    plain_text = re.sub(r'\*|_|~|`', '', text)  # remove markdown formatting
    # (optional) keep links inside text, no markup
    return plain_text

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
                # get original msg
                msg = await context.bot.forward_message(
                    chat_id=update.effective_chat.id,
                    from_chat_id=BACKUP_CHANNEL,
                    message_id=msg_id
                )
                await msg.delete()

                if msg.text:
                    cleaned = clean_text_keep_links(msg.text, REMOVE_TEXT)
                    await context.bot.send_message(MAIN_CHANNEL, text=cleaned)

                elif msg.caption:
                    cleaned = clean_text_keep_links(msg.caption, REMOVE_TEXT)
                    if msg.photo:
                        await context.bot.send_photo(MAIN_CHANNEL, msg.photo[-1].file_id, caption=cleaned)
                    elif msg.video:
                        await context.bot.send_video(MAIN_CHANNEL, msg.video.file_id, caption=cleaned)
                    elif msg.document:
                        await context.bot.send_document(MAIN_CHANNEL, msg.document.file_id, caption=cleaned)
                    else:
                        await context.bot.send_message(MAIN_CHANNEL, text=cleaned)

                else:
                    # fallback if no text/caption
                    await context.bot.copy_message(MAIN_CHANNEL, BACKUP_CHANNEL, msg_id)

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
