import os
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import requests
import asyncio

TOKEN = "8475035371:AAEHrLg27kR8_g-vCROvMVrbfoSixCXaxcA"
ADMIN_ID = 5997715263  # <-- তোমার Telegram numeric ID

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

# --- VIDEO API (ytmp3 / tiktok / etc) ---
def fetch_video(url):
    try:
        api = f"https://ytmp3.as/tikmp4?url={url}"
        res = requests.get(api).json()
        if res.get("status") == "ok":
            return res["url"], res["title"]
        return None, None
    except:
        return None, None


# === FASTAPI KEEP-ALIVE ===
@app.get("/")
def home():
    return {"status": "running"}


# === START COMMAND ===
@dp.message(commands=["start"])
async def start(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Add bot to group", url=f"https://t.me/{(await bot.get_me()).username}?startgroup=true")
    kb.button(text="💬 Developer", url="https://t.me/YOUR_USERNAME")

    await message.answer(
        f"👋 Hi {message.from_user.full_name}!\n\n"
        "🎥 Just send me any **Video URL** (TikTok, YouTube, IG, FB)\n"
        "I will download it for you ✅",
        reply_markup=kb.as_markup()
    )


# === BROADCAST (admin only) ===
@dp.message(commands=["broadcast"])
async def broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("❌ You are not admin.")

    text = message.text.replace("/broadcast ", "")
    count = 0

    async for user in bot.get_chat_members(chat_id=message.chat.id):
        try:
            await bot.send_message(user.user.id, text)
            count += 1
        except:
            pass

    await message.reply(f"✅ Successfully sent to `{count}` users.")


# === DOWNLOAD VIDEO ===
@dp.message()
async def download(message: types.Message):
    url = message.text.strip()

    await message.reply("⏳ Fetching video... Please wait...")

    video_url, title = fetch_video(url)

    if video_url:
        await bot.send_video(
            chat_id=message.chat.id,
            video=video_url,
            caption=f"✅ **Downloaded Successfully!**\n🎬 Title: `{title}`"
        )
    else:
        await message.reply("❌ Failed to fetch video. Make sure URL is correct.")


# === START THE BOT ===
async def main():
    async with bot:
        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
