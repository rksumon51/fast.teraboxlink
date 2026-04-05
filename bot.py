import os
import requests
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

PLAYER_URL = "https://final-terabox-bot.vercel.app"

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Send Terabox link")

# ================= AUTO FIX =================
def fix_link(url):
    url = url.strip()

    # 🔥 fix domains
    url = url.replace("terasharefile.com", "www.terabox.com")
    url = url.replace("1024terabox.com", "www.terabox.com")
    url = url.replace("terabox.app", "www.terabox.com")

    return url

# ================= API 1 =================
def api1(url):
    try:
        res = requests.post(
            "https://iteraplay.com/api/stream",
            json={"url": url},
            timeout=15
        )
        data = res.json()
        if data.get("success"):
            return data.get("data")
    except:
        return None

# ================= API 2 =================
def api2(url):
    try:
        res = requests.get(
            f"https://terabox-downloader-api.vercel.app/api?url={url}",
            timeout=15
        )
        data = res.json()
        if data.get("success"):
            return {
                "normal_dlink": data["data"].get("download"),
                "file_name": data["data"].get("filename"),
                "size": data["data"].get("size"),
                "thumb": data["data"].get("thumbnail"),
            }
    except:
        return None

# ================= API 3 (EXTRA BACKUP) =================
def api3(url):
    try:
        res = requests.get(
            f"https://api.vevioz.com/api/button/mp4?url={url}",
            timeout=15
        )
        if "href=" in res.text:
            return {
                "normal_dlink": url,
                "file_name": "video.mp4",
                "size": "Unknown",
                "thumb": None,
            }
    except:
        return None

# ================= MAIN =================
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_url = update.message.text
    url = fix_link(raw_url)

    msg = await update.message.reply_text("⚡ Fetching video...")

    try:
        file = None

        # 🔥 API 1
        file = api1(url)

        # 🔁 API 2
        if not file:
            file = api2(url)

        # 🔁 API 3
        if not file:
            file = api3(url)

        if not file:
            return await msg.edit_text("❌ All APIs failed")

        download_url = file.get("normal_dlink")
        file_name = file.get("file_name", "video.mp4")
        size = file.get("size", "Unknown")
        thumb = file.get("thumb")

        if not download_url:
            return await msg.edit_text("❌ No download link")

        # ================= SUPER FAST SEND =================
        try:
            await update.message.reply_video(
                video=download_url,
                caption=f"🎬 {file_name}\n📦 {size}"
            )
            return await msg.delete()
        except:
            pass

        # ================= FALLBACK =================
        encoded = urllib.parse.quote(download_url, safe="")
        player_link = f"{PLAYER_URL}?url={encoded}"

        buttons = [
            [InlineKeyboardButton("⬇️ Download", url=download_url)],
            [InlineKeyboardButton("🎬 Watch Online", url=player_link)]
        ]

        caption = f"""✅ Completed

🎬 {file_name}
📦 {size}
"""

        if thumb:
            await update.message.reply_photo(
                photo=thumb,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await msg.edit_text(caption, reply_markup=InlineKeyboardMarkup(buttons))

    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")

# ================= RUN =================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

print("🚀 PRO Bot Running...")
app.run_polling()
