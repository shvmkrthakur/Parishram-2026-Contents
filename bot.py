#!/usr/bin/env python3
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.helpers import escape, escape_html

# ---------------- CONFIG ----------------
BOT_TOKEN = "7947639550:AAHEtB3KRztXvgDfXM-r3-mWRCA8Vn-G5_g"
BACKUP_CHANNEL = "@gdndndm"        # source channel username
MAIN_CHANNEL   = -1002371985459    # target channel id
REMOVE_TEXT    = "✨ Powered By : @ParishramZone"
# ----------------------------------------

logging.basicConfig(level=logging.INFO)


def clean_html(msg, remove_text):
    """Convert message to HTML, remove unwanted text, keep all links."""
    if msg.text_html:
        html = msg.text_html
    elif msg.caption_html:
        html = msg.caption_html
    else:
        return None

    # remove unwanted promo text
    html = html.replace(remove_text, "").strip()
    return html


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
                # fetch original msg (forward to get content)
                fwd = await context.bot.forward_message(
                    chat_id=update.effective_chat.id,
                    from_chat_id=BACKUP_CHANNEL,
                    message_id=msg_id
                )

                cleaned_html = clean_html(fwd, REMOVE_TEXT)

                if fwd.text:
                    await context.bot.send_message(
                        MAIN_CHANNEL,
                        text=cleaned_html,
                        parse_mode="HTML"
                    )

                elif fwd.caption:
                    if fwd.photo:
                        await context.bot.send_photo(
                            MAIN_CHANNEL,
                            fwd.photo[-1].file_id,
                            caption=cleaned_html,
                            parse_mode="HTML"
                        )
                    elif fwd.video:
                        await context.bot.send_video(
                            MAIN_CHANNEL,
                            fwd.video.file_id,
                            caption=cleaned_html,
                            parse_mode="HTML"
                        )
                    elif fwd.document:
                        await context.bot.send_document(
                            MAIN_CHANNEL,
                            fwd.document.file_id,
                            caption=cleaned_html,
                            parse_mode="HTML"
                        )
                    else:
                        await context.bot.send_message(
                            MAIN_CHANNEL,
                            text=cleaned_html,
                            parse_mode="HTML"
                        )

                else:
                    await context.bot.copy_message(MAIN_CHANNEL, BACKUP_CHANNEL, msg_id)

                # delete temp forward
                await fwd.delete()

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
