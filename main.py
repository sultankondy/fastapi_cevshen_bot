import os
import datetime
from fastapi import FastAPI, Request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = -1002394763684  # fallback if not detected from group

# Global variable to store detected group chat ID
group_chat_id = None

# Telegram Bot Setup
bot = Bot(token=BOT_TOKEN)
app = FastAPI()
scheduler = AsyncIOScheduler()

# Initialize Telegram Application once
application = Application.builder().token(BOT_TOKEN).build()

# Names and ranges for polls
names = ["Sultan", "Muhit", "Rustem", "Shadiar", "Dias", "Daniel", "Kuanysh"]
ranges = ["1-15", "16-30", "31-45", "46-60", "61-75", "76-90", "91-100 + dua"]

# Daily poll generation logic
def generate_poll_options():
    today = datetime.date.today()
    weekday = today.weekday()  # 0=Monday, 1=Tuesday, ..., 6=Sunday
    sultan_index = names.index("Sultan")
    shift = (sultan_index - ((weekday - 2) % 7)) % 7
    rotated_names = names[shift:] + names[:shift]
    options = [f"{name} {rng}" for name, rng in zip(rotated_names, ranges)]
    title = today.strftime("%B %d")
    return title, options

# Function to send the daily poll
async def send_daily_poll():
    title, options = generate_poll_options()
    target_chat_id = group_chat_id or CHAT_ID

    if not target_chat_id:
        print("⚠️ No chat ID available to send the poll.")
        return

    await bot.send_poll(
        chat_id=target_chat_id,
        question=title,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=False
    )

# FastAPI root route
@app.get("/")
def root():
    return {"message": "Bot is running."}

# Webhook route
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    print("Incoming update:", data)
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"status": "ok"}

# # /start command handler
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     chat_id = update.effective_chat.id
#     print(f"Chat ID: {chat_id}")

#     # Generate poll for current day
#     title, options = generate_poll_options()

#     # Send the poll immediately
#     await bot.send_poll(
#         chat_id=chat_id,
#         question=title,
#         options=options,
#         is_anonymous=False,
#         allows_multiple_answers=False
#     )

# # Register handler
# application.add_handler(CommandHandler("start", start))

# On startup
@app.on_event("startup")
async def startup_event():
    webhook_url = "https://cevshenbot-production.up.railway.app:80/webhook"
    await bot.set_webhook(webhook_url)
    print("Webhook set successfully.")
    print(CHAT_ID)

    scheduler.add_job(send_daily_poll, 'interval', days=1, start_date='2025-04-09 09:00:00')
    scheduler.start()

# On shutdown
@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    scheduler.shutdown()
    print("Bot stopped.")

# Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



