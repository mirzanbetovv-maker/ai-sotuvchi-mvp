import os
import asyncio
import logging
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from groq import Groq
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
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
ORDERS_FILE = BASE_DIR / "orders.txt"

PRODUCT, COLOR, MEMORY, PHONE, CONFIRM = range(5)


def read_products():
    try:
        return PRODUCTS_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "Mahsulotlar ro'yxati topilmadi."


def save_order(user, product, color, memory, phone):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    order_text = (
        "\n============================\n"
        f"Sana: {now}\n"
        f"Telegram ID: {user.id}\n"
        f"Username: @{user.username or 'yoq'}\n"
        f"Ism: {user.first_name or 'yoq'}\n"
        f"Mahsulot: {product}\n"
        f"Rang: {color}\n"
        f"Xotira: {memory}\n"
        f"Telefon: {phone}\n"
    )

    with open(ORDERS_FILE, "a", encoding="utf-8") as file:
        file.write(order_text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men AI Telefon Sotuvchiman 🤖📱\n\n"
        "Telefonlar haqida savol berishingiz mumkin.\n"
        "Buyurtma berish uchun /buyurtma"
    )


def ask_groq(text):
    products = read_products()

    system_prompt = f"""
Sen professional AI telefon sotuvchisan.

Mijoz bilan o'zbek tilida sodda, qisqa va muloyim gaplash.

DO'KONDAGI TELEFONLAR:

{products}

QOIDALAR:
- Narxlarni faqat yuqoridagi ro'yxatdan ol.
- Narxni o'zing o'ylab topma.
- Ro'yxatda yo'q telefonni mavjud deb aytma.
- Mijozning budjetiga mos telefon tavsiya qil.
- Kamera, RAM, xotira, batareya va boshqa xususiyatlarni
  faqat ro'yxatdagi ma'lumotlardan ayt.
- Bir nechta telefonni taqqoslash mumkin.
- Mijoz sotib olmoqchi bo'lsa /buyurtma buyrug'ini yuborishini ayt.
- Ma'lumot ro'yxatda bo'lmasa, ma'lumot yo'qligini ochiq ayt.
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


async def ai_message_handler(
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


async def order_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "Buyurtma berishni boshladik ✅\n\n"
        "Qaysi telefonni sotib olmoqchisiz?"
    )

    return PRODUCT


async def order_product(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["product"] = update.message.text

    await update.message.reply_text(
        "Qaysi rangni xohlaysiz?"
    )

    return COLOR


async def order_color(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["color"] = update.message.text

    await update.message.reply_text(
        "Qaysi xotira variantini xohlaysiz?\n"
        "Masalan: 128 GB yoki 256 GB"
    )

    return MEMORY


async def order_memory(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["memory"] = update.message.text

    await update.message.reply_text(
        "Telefon raqamingizni yozing.\n"
        "Masalan: +998901234567"
    )

    return PHONE


async def order_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["phone"] = update.message.text

    product = context.user_data["product"]
    color = context.user_data["color"]
    memory = context.user_data["memory"]
    phone = context.user_data["phone"]

    await update.message.reply_text(
        "Buyurtmangiz:\n\n"
        f"📱 Telefon: {product}\n"
        f"🎨 Rang: {color}\n"
        f"💾 Xotira: {memory}\n"
        f"📞 Telefon raqam: {phone}\n\n"
        "Tasdiqlash uchun HA yozing.\n"
        "Bekor qilish uchun YOQ yozing."
    )

    return CONFIRM


async def order_confirm(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    answer = update.message.text.strip().lower()

    if answer in ["ha", "yes", "ok", "tasdiqlayman"]:
        save_order(
            update.effective_user,
            context.user_data["product"],
            context.user_data["color"],
            context.user_data["memory"],
            context.user_data["phone"],
        )

        await update.message.reply_text(
            "Buyurtmangiz qabul qilindi ✅\n"
            "Tez orada siz bilan bog'lanamiz."
        )

    else:
        await update.message.reply_text(
            "Buyurtma bekor qilindi."
        )

    context.user_data.clear()

    return ConversationHandler.END


async def cancel_order(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    context.user_data.clear()

    await update.message.reply_text(
        "Buyurtma bekor qilindi."
    )

    return ConversationHandler.END


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    order_handler = ConversationHandler(
        entry_points=[
            CommandHandler("buyurtma", order_start)
        ],
        states={
            PRODUCT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    order_product,
                )
            ],
            COLOR: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    order_color,
                )
            ],
            MEMORY: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    order_memory,
                )
            ],
            PHONE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    order_phone,
                )
            ],
            CONFIRM: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    order_confirm,
                )
            ],
        },
        fallbacks=[
            CommandHandler("bekor", cancel_order)
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(order_handler)

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            ai_message_handler,
        )
    )

    render_url = os.getenv("RENDER_EXTERNAL_URL")

    if render_url:
        port = int(os.getenv("PORT", "10000"))

        print("AI Telefon Sotuvchi Render webhook bilan ishga tushdi.")

        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=BOT_TOKEN,
            webhook_url=f"{render_url}/{BOT_TOKEN}",
        )

    else:
        print("AI Telefon Sotuvchi lokal rejimda ishga tushdi.")
        app.run_polling()


if __name__ == "__main__":
    main()
