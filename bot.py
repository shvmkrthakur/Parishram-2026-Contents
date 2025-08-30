#!/usr/bin/env python3
import logging
from telegram import Update, MessageEntity
from telegram.ext import Application, CommandHandler, ContextTypes

# ---------------- CONFIG ----------------
BOT_TOKEN = "7947639550:AAHEtB3KRztXvgDfXM-r3-mWRCA8Vn-G5_g"
BACKUP_CHANNEL = "@gdndndm"        # source channel username
MAIN_CHANNEL   = -1002371985459    # target channel id
REMOVE_TEXT    = "✨ Powered By : @ParishramZone"
# ----------------------------------------

logging.basicConfig(level=logging.INFO)


def clean_text_and_entities(msg, remove_text):
    """Remove unwanted text, adjust entity offsets, keep all links."""
    text = msg.text or msg.caption
    entities = msg.entities or msg.caption_entities

    if not text:
        return None, None

    # --- step 1: remove unwanted text ---
    remove_start = text.find(remove_text)
    remove_end = remove_start + len(remove_text) if remove_start != -1 else -1

    new_text = text.replace(remove_text, "").strip()

    # --- step 2: adjust entity offsets ---
    safe_entities = []
    if entities:
        for e in entities:
            if e.type in ["url", "text_link"]:  # keep all links
                offset = e.offset
                length = e.length

                # shift if removal before entity
                if remove_start != -1 and offset > remove_start:
                    offset -= len(remove_text)

                # skip broken entities
                if offset + length <= len(new_text):
                    safe_entities.append(
                        MessageEntity(
                            type=e.type,
                            offset=offset,
                            length=length,
                            url=e.url
                        )
                    )

    return new_text, safe_entities


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
                # temporary forward (to read original msg fully)
                fwd = await context.bot.forward_message(
                    chat_id=update.effective_chat.id,
                    from_chat_id=BACKUP_CHANNEL,
                    message_id=msg_id
                )

                # clean text + entities
                cleaned_text, safe_entities = clean_text_and_entities(fwd, REMOVE_TEXT)

                if fwd.text:
                    await context.bot.send_message(
                        MAIN_CHANNEL,
                        text=cleaned_text,
                        entities=safe_entities
                    )

                elif fwd.caption:
                    if fwd.photo:
                        await context.bot.send_photo(
                            MAIN_CHANNEL,
                            fwd.photo[-1].file_id,
                            caption=cleaned_text,
                            caption_entities=safe_entities
                        )
                    elif fwd.video:
                        await context.bot.send_video(
                            MAIN_CHANNEL,
                            fwd.video.file_id,
                            caption=cleaned_text,
                            caption_entities=safe_entities
                        )
                    elif fwd.document:
                        await context.bot.send_document(
                            MAIN_CHANNEL,
                            fwd.document.file_id,
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
