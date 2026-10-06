# AI Sotuvchi MVP

Telegram mijoz -> Python bot -> Claude -> Google Apps Script -> Google Sheets
                                      -> sotuvchiga Telegram xabari

MVP:
- mijoz savollariga Claude orqali javob beradi;
- Products jadvalidan mahsulot/narx/ombor ma'lumotini oladi;
- buyurtma uchun ism, telefon, manzilni yig'adi;
- buyurtmani Orders jadvaliga yozadi;
- sotuvchining Telegram chatiga yangi buyurtma haqida xabar yuboradi.

Muhim:
- Claude API kaliti kerak. API ishlatilishi billingga bog'liq.
- Telegram bot tokeni va Claude API kalitini hech kimga ochiq yubormang.

## 1. Telegram
@BotFather -> /newbot -> token oling.

## 2. Claude API
Anthropic API key yarating.

## 3. Google Sheet
Yangi Google Sheet yarating. Ikki varaq:
Products
Orders

Products 1-qator:
id | name | price | stock | description | active

Misol:
001 | Redmi Buds 5 | 350000 | 8 | Simsiz quloqchin | TRUE
002 | Type-C kabel | 50000 | 25 | Tez zaryad kabeli | TRUE

Orders 1-qator:
order_id | date | customer_name | phone | address | product | quantity | total | status | telegram_user_id

## 4. Apps Script
Google Sheet -> Extensions -> Apps Script.
apps_script.gs kodini joylang.
CONFIG_SECRET ni o'zgartiring.
Deploy -> New deployment -> Web app.
Execute as: Me
Who has access: Anyone with the link
URL ni .env ga yozing.

## 5. Windows
Python 3.11+ o'rnating.
CMD:
  cd ai_sotuvchi_mvp
  py -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt
  copy .env.example .env

.env ni to'ldiring.

## 6. Sotuvchi chat ID
Botga sotuvchining Telegram akkauntidan /start yuboring.
So'ng brauzerda:
https://api.telegram.org/botBOT_TOKEN/getUpdates
ochib chat.id ni toping.
SELLER_CHAT_ID ga yozing.

## 7. Ishga tushirish
  .venv\Scripts\activate
  python main.py

Telegramda botga /start yuboring va test qiling.

Keyingi bosqich:
Instagram/WhatsApp, to'lov, omborni avtomatik kamaytirish,
qayta sotuv eslatmalari, kunlik AI hisobot va sotuvchi paneli.
