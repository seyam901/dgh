import os
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import requests
import asyncio

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()


# --- VIDEO DOWNLOAD API ---
def fetch_video(url):
    try:
        api = f"https://ytmp3.as/tikmp4?url={url}"
        res = requests.get(api).json()
        if res.get("status") == "ok":
            return res["url"], res["title"]
        return None, None
    except:
        return None, None


@app.get("/")
def alive():
    return {"status": "running", "bot": "✅ online"}


@dp.message(commands=["start"])
async def start(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Add to group", url=f"https://t.me/{(await bot.get_me()).username}?startgroup=true")
    kb.button(text="👨‍💻 Developer", url="https://t.me/YOUR_USERNAME")

    await message.answer(
        f"👋 Hi {message.from_user.full_name}!\n\n"
        "✅ Send any video link:\n"
        "• TikTok\n• YouTube\n• Facebook\n• Instagram\n\n"
        "⚡ I’ll download it for you!",
        reply_markup=kb.as_markup()
    )


@dp.message(commands=["broadcast"])
async def broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("❌ You are not admin.")

    text = message.text.replace("/broadcast ", "")
    await message.answer("📢 Broadcasting...")

    async for dialog in bot.get_dialogs():
        try:
            await bot.send_message(dialog.chat.id, text)
        except:
            pass

    await message.answer("✅ Broadcast completed!")


@dp.message()
async def download(message: types.Message):
    url = message.text.strip()
    wait_msg = await message.reply("⏳ Fetching video...")

    video_url, title = fetch_video(url)

    if video_url:
        await message.reply_video(video_url, caption=f"✅ Downloaded\n🎬 `{title}`")
    else:
        await message.reply("❌ Video download failed!")

    await wait_msg.delete()


async def main():
    async with bot:
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
