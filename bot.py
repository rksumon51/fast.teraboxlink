import os
import requests
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

PLAYER_URL = "https://api.allorigins.win/raw?url="

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*"
}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Send Terabox link")

# ================= FIX LINK =================
def fix_link(url):
    url = url.strip()

    # domain fix
    url = url.replace("terasharefile.com", "www.terabox.com")
    url = url.replace("1024terabox.com", "www.terabox.com")
    url = url.replace("terabox.app", "www.terabox.com")

    # redirect follow
    try:
        r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
        url = r.url
    except:
        pass

    return url

# ================= API 1 =================
def api1(url):
    try:
        res = requests.post(
            "https://iteraplay.com/api/stream",
            json={"url": url},
            headers=HEADERS,
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
            headers=HEADERS,
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

# ================= API 3 (backup scraper) =================
def api3(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if ".mp4" in res.text:
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

        # 🔥 Try APIs (priority system)
        for api in [api1, api2, api3]:
            file = api(url)
            if file:
                break

        if not file:
            return await msg.edit_text("❌ All APIs failed")

        download_url = file.get("normal_dlink")
        file_name = file.get("file_name", "video.mp4")
        size = file.get("size", "Unknown")
        thumb = file.get("thumb")

        if not download_url:
            return await msg.edit_text("❌ No download link")

        # 🔥 PROXY FIX (MOST IMPORTANT)
        proxy_url = PLAYER_URL + urllib.parse.quote(download_url, safe="")

        # ================= DIRECT SEND =================
        try:
            await update.message.reply_video(
                video=proxy_url,
                caption=f"🎬 {file_name}\n📦 {size}",
                supports_streaming=True
            )
            return await msg.delete()
        except:
            pass

        # ================= FALLBACK =================
        buttons = [
            [InlineKeyboardButton("⬇️ Download", url=download_url)],
            [InlineKeyboardButton("🎬 Watch Online", url=proxy_url)]
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

print("🚀 ULTRA PRO Bot Running...")

app.run_polling()
