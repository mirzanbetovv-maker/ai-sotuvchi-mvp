import os
import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN topilmadi")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY topilmadi")

client = Groq(api_key=GROQ_API_KEY)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

BASE_DIR = Path(__file__).resolve().parent
PRODUCTS_FILE = BASE_DIR / "products.txt"


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "Salom! Men AI Sotuvchiman 🤖\n"
        "Mahsulotlarimiz haqida savol berishingiz mumkin."
    )


def ask_groq(text):
    try:
        products = PRODUCTS_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        products = "Mahsulotlar ro'yxati topilmadi."

    system_prompt = f"""
Sen professional AI sotuvchisan.

Mijoz bilan o'zbek tilida sodda, qisqa va muloyim gaplash.

DO'KONDAGI MAHSULOTLAR:

{products}

QOIDALAR:
- Narxlarni faqat yuqoridagi ro'yxatdan ol.
- Narxni o'zing o'ylab topma.
- Mavjud bo'lmagan mahsulotni mavjud deb aytma.
- Mijozga mos mahsulot tavsiya qil.
- Mijoz sotib olmoqchi bo'lsa mahsulot nomini aniqlashtir.
- Kerak bo'lsa rang va o'lchamini so'ra.
- Ro'yxatda ma'lumot bo'lmasa, ma'lumot yo'qligini ayt.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        temperature=0.4,
        max_tokens=500,
    )

    return response.choices[0].message.content


async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    try:
        answer = await asyncio.to_thread(
            ask_groq,
            update.message.text
        )

        await update.message.reply_text(
            answer or "Javob olinmadi."
        )

    except Exception:
        logging.exception("Groq xatosi")

        await update.message.reply_text(
            "AI serverida vaqtinchalik muammo. "
            "Birozdan keyin yana urinib ko'ring."
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    render_url = os.getenv("RENDER_EXTERNAL_URL")

    if render_url:
        port = int(os.getenv("PORT", "10000"))

        print("AI Sotuvchi Render webhook bilan ishga tushdi.")

        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=BOT_TOKEN,
            webhook_url=f"{render_url}/{BOT_TOKEN}",
        )

    else:
        print("AI Sotuvchi lokal rejimda ishga tushdi.")
        app.run_polling()


if __name__ == "__main__":
    main()