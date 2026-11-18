
import os
import re
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ["BOT_TOKEN"]

# O'zbekcha shubhali iboralar
SPAM_PATTERNS = [
    r"pul\s+yuvish",
    r"pul\s+aylantirish",
    r"pul\s+aylantirib\s+ber",
    r"pul\s+otkazib\s+ber",
    r"pul\s+kochirib\s+ber",
    r"kartangizni\s+ijaraga",
    r"karta\s+ijaraga",
    r"karta\s+kerak",
    r"hisobingizdan\s+pul",
    r"kartadan\s+kartaga",
    r"naqdlashtirib\s+ber",
    r"obnal",
    r"drop\s+karta",
    r"foizga\s+pul\s+ber",
    r"tez\s+daromad",
]

COMPILED_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in SPAM_PATTERNS
]


def normalize(text):
    text = text.lower()
    text = text.replace("'", "")
    text = text.replace("‘", "")
    text = text.replace("ʻ", "")
    text = text.replace("’", "")
    text = re.sub(r"[^a-zа-яё0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Uzbek Spam Guard ishga tayyor. "
        "Guruhda spam xabarlarni tekshiraman."
    )


async def check_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not message or not chat or not user:
        return

    if chat.type not in ("group", "supergroup"):
        return

    if user.is_bot:
        return

    # Guruh administratorlariga tegmaydi
    try:
        member = await chat.get_member(user.id)
        if member.status in ("administrator", "creator"):
            return
    except Exception:
        logging.exception("Admin holatini tekshirishda xato")
        return

    content = message.text or message.caption or ""
    if not content:
        return

    clean_text = normalize(content)

    for pattern in COMPILED_PATTERNS:
        if pattern.search(clean_text):
            try:
                await message.delete()
                logging.info(
                    "Spam xabar o'chirildi: %s",
                    user.id
                )
            except Exception:
                logging.exception("Xabarni o'chirishda xato")
            return


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.CAPTION) & ~filters.COMMAND,
            check_message
        )
    )

    logging.info("Uzbek Spam Guard ishga tushdi")
    app.run_polling()


if __name__ == "__main__":
    main()

