import os
import asyncio
import logging

from dotenv import load_dotenv
from google import genai
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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN topilmadi")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY topilmadi")

client = genai.Client(api_key=GEMINI_API_KEY)

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men AI Sotuvchiman 🤖\n"
        "Mahsulotlarimiz haqida savol berishingiz mumkin."
    )


def ask_gemini(text):
    try:
        with open("products.txt", "r", encoding="utf-8") as file:
            products = file.read()
    except FileNotFoundError:
        products = "Mahsulotlar ro'yxati topilmadi."

    prompt = f"""
Sen professional AI sotuvchisan.

Mijoz bilan o'zbek tilida sodda, qisqa va muloyim gaplash.

DO'KONDAGI MAHSULOTLAR:

{products}

QOIDALAR:

- Narxlarni faqat mahsulotlar ro'yxatidan ol.
- Narxlarni o'zing o'ylab topma.
- Mavjud bo'lmagan mahsulotni mavjud deb aytma.
- Mijozga mos mahsulot tavsiya qil.
- Mijoz sotib olmoqchi bo'lsa, mahsulot nomi,
  rangi va o'lchamini aniqlashtir.
- Agar kerakli ma'lumot ro'yxatda bo'lmasa,
  bu ma'lumot mavjud emasligini ayt.

MIJOZNING XABARI:

{text}
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )

    return response.text


async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    try:
        answer = await asyncio.to_thread(
            ask_gemini,
            update.message.text
        )

        await update.message.reply_text(
            answer or "Javob olinmadi."
        )

    except Exception:
        logging.exception("Gemini xatosi")
        await update.message.reply_text(
            "Texnik muammo yuz berdi."
        )


def main():
    def main():
    port = int(os.environ.get("PORT", "10000"))
    render_url = os.environ.get("RENDER_EXTERNAL_URL")

    if not render_url:
        raise RuntimeError("RENDER_EXTERNAL_URL topilmadi")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    print("AI Sotuvchi Render webhook bilan ishga tushdi.")

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=BOT_TOKEN,
        webhook_url=f"{render_url}/{BOT_TOKEN}",
    )


if __name__ == "__main__":
    main()