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
