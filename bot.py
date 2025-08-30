#!/usr/bin/env python3
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ---------------- CONFIG ----------------
BOT_TOKEN = "7947639550:AAHEtB3KRztXvgDfXM-r3-mWRCA8Vn-G5_g"
BACKUP_CHANNEL = "@gdndndm"        # backup channel username
MAIN_CHANNEL   = -1002371985459    # target channel id (ID रखना ज्यादा safe है)
REMOVE_TEXT    = "✨ Powered By : @ParishramZone"
# ----------------------------------------

logging.basicConfig(level=logging.INFO)

def clean_text_and_entities(msg, remove_text):
    """Remove unwanted text, drop formatting but keep links only."""
    text = msg.text or msg.caption
    entities = msg.entities or msg.caption_entities

    if not text:
        return None, None

    # remove unwanted promo
    text = text.replace(remove_text, "").strip()

    safe_entities = []
    if entities:
        for e in entities:
            if e.type in ["url", "text_link"]:  # keep only links
                if e.offset + e.length <= len(text):
                    safe_entities.append(e)

    return text, safe_entities


# /start 1-100
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
                # fetch message directly
                msg = await context.bot.get_chat(BACKUP_CHANNEL).get_message(msg_id)

                # clean text + entities
                cleaned_text, safe_entities = clean_text_and_entities(msg, REMOVE_TEXT)

                if msg.text:
                    await context.bot.send_message(
                        MAIN_CHANNEL,
                        text=cleaned_text,
                        entities=safe_entities
                    )

                elif msg.caption:
                    if msg.photo:
                        await context.bot.send_photo(
                            MAIN_CHANNEL,
                            msg.photo[-1].file_id,
                            caption=cleaned_text,
                            caption_entities=safe_entities
                        )
                    elif msg.video:
                        await context.bot.send_video(
                            MAIN_CHANNEL,
                            msg.video.file_id,
                            caption=cleaned_text,
                            caption_entities=safe_entities
                        )
                    elif msg.document:
                        await context.bot.send_document(
                            MAIN_CHANNEL,
                            msg.document.file_id,
                            caption=cleaned_text,
                            caption_entities=safe_entities
                        )
                    else:
                        await context.bot.send_message(
                            MAIN_CHANNEL,
                            text=cleaned_text,
                            entities=safe_entities
                        )

                else:
                    # fallback: raw copy
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
