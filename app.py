import os
import json
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Database file
DB_FILE = "database.json"

# Initialize Express-like web server (for Koyeb health checks)
from aiohttp import web
async def web_handler(request):
    return web.Response(text="Bot is running")

app = web.Application()
app.add_routes([web.get('/', web_handler)])

# Load database
def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save database
def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_msg = f"""Hello, {user.username or user.first_name}!

Welcome to the URL Shortener Bot!
You can use this bot to shorten URLs using the mybios.eu.org service.

To shorten a URL, just type or paste the URL directly in the chat.

If you haven't set your API token yet, use:
/setapi YOUR_API_TOKEN

Now, go ahead and try it out!"""
    
    await update.message.reply_text(welcome_msg)

async def set_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        api_token = context.args[0]
        chat_id = str(update.effective_chat.id)
        
        db = load_db()
        db[chat_id] = api_token
        save_db(db)
        
        await update.message.reply_text(f"API token set successfully!")
    except IndexError:
        await update.message.reply_text("Please provide an API token!\nUsage: /setapi YOUR_API_TOKEN")

# URL handler
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    url = update.message.text
    
    db = load_db()
    api_token = db.get(chat_id)
    
    if not api_token:
        await update.message.reply_text("Please set your API token first using /setapi")
        return
    
    try:
        response = requests.get(
            "https://blog.thunderlinks.site/api",
            params={"api": api_token, "url": url}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                await update.message.reply_text(f"Shortened URL: {data['shortenedUrl']}")
            else:
                await update.message.reply_text("Error shortening URL. Please check your API token.")
        else:
            await update.message.reply_text("API request failed. Please try again later.")
            
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("An error occurred while processing your request.")

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error: {context.error}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="An error occurred. Please try again."
    )

def main():
    # Create Application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setapi", set_api))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Run bot and web server
    application.run_polling()
    web.run_app(app, port=3000)

if __name__ == "__main__":
    main()
