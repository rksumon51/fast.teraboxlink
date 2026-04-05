import os
import requests
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

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

    url = url.replace("terasharefile.com", "www.terabox.com")
    url = url.replace("1024terabox.com", "www.terabox.com")
    url = url.replace("terabox.app", "www.terabox.com")

    try:
        session = requests.Session()
        r = session.get(url, headers=HEADERS, allow_redirects=True, timeout=15)
        url = r.url
    except:
        pass

    print("FINAL URL:", url)
    return url

# ================= RETRY SYSTEM =================
def try_api(api, url):
    for _ in range(2):
        try:
            data = api(url)
            if data:
                return data
        except:
            continue
    return None

# ================= API 1 =================
def api1(url):
    res = requests.post(
        "https://iteraplay.com/api/stream",
        json={"url": url},
        headers=HEADERS,
        timeout=15
    )
    data = res.json()
    if data.get("success"):
        return data.get("data")

# ================= API 2 =================
def api2(url):
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

# ================= API 3 =================
def api3(url):
    res = requests.get(url, headers=HEADERS, timeout=10)
    if ".mp4" in res.text:
        return {
            "normal_dlink": url,
            "file_name": "video.mp4",
            "size": "Unknown",
            "thumb": None,
        }

# ================= MAIN =================
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_url = update.message.text
    url = fix_link(raw_url)

    msg = await update.message.reply_text("⚡ Fetching video...")

    try:
        file = None

        for api in [api1, api2, api3]:
            file = try_api(api, url)
            if file:
                break

        if not file:
            return await msg.edit_text(
                "❌ Failed\n\n🔒 Link may be private / expired\n\n👉 Try another link"
            )

        download_url = file.get("normal_dlink")
        file_name = file.get("file_name", "video.mp4")
        size = file.get("size", "Unknown")
        thumb = file.get("thumb")

        if not download_url:
            return await msg.edit_text("❌ No video link found")

        # ================= DIRECT SEND =================
        try:
            await update.message.reply_video(
                video=download_url,
                caption=f"🎬 {file_name}\n📦 {size}",
                supports_streaming=True
            )
            return await msg.delete()
        except:
            pass

        # ================= FALLBACK =================
        buttons = [
            [InlineKeyboardButton("⬇️ Download", url=download_url)]
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

print("🚀 FINAL BOT RUNNING...")

app.run_polling()
