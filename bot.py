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
                # fetch original message
                original = await context.bot.forward_message(
                    chat_id=update.effective_chat.id,
                    from_chat_id=BACKUP_CHANNEL,
                    message_id=msg_id
                )
                await original.delete()  # delete test forward

                msg = await context.bot.get_chat(BACKUP_CHANNEL)
            except:
                # try with get_messages and resend clean
                try:
                    original = await context.bot.get_chat(BACKUP_CHANNEL)
                except Exception as e:
                    await update.message.reply_text(f"❌ Error on {msg_id}: {e}")
                    continue

            try:
                m = await context.bot.copy_message(
                    chat_id=MAIN_CHANNEL,
                    from_chat_id=BACKUP_CHANNEL,
                    message_id=msg_id
                )

                # clean text/caption
                if m.text:
                    cleaned_text = m.text.replace(REMOVE_TEXT, "").strip()
                    if cleaned_text != m.text:
                        await context.bot.edit_message_text(
                            chat_id=MAIN_CHANNEL,
                            message_id=m.message_id,
                            text=cleaned_text
                        )
                elif m.caption:
                    cleaned_caption = m.caption.replace(REMOVE_TEXT, "").strip()
                    if cleaned_caption != m.caption:
                        await context.bot.edit_message_caption(
                            chat_id=MAIN_CHANNEL,
                            message_id=m.message_id,
                            caption=cleaned_caption
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
