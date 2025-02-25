import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Start command
def start(update: Update, context: CallbackContext) -> None:
    start_message = """
    🌟 *Welcome to the URL Shortener Bot!* 🌟

    This bot helps you shorten URLs using the AdLinkFly API.

    📌 *Commands:*
    /start - Start the bot and see this message
    /help - Get help and see all commands
    /shorten - Shorten a URL

    🔗 *How to Use:*
    1. Send /shorten command
    2. Provide your API key
    3. Provide the URL you want to shorten

    📝 *Note:* Your API key will be stored securely for future use.

    Enjoy shortening your URLs! 🚀
    """
    update.message.reply_text(start_message, parse_mode='Markdown')

# Help command
def help_command(update: Update, context: CallbackContext) -> None:
    help_message = """
    📚 *Help Section*

    Here are the commands you can use:

    /start - Start the bot and see the welcome message
    /help - Get help and see all commands
    /shorten - Shorten a URL

    🔗 *How to Use:*
    1. Send /shorten command
    2. Provide your API key
    3. Provide the URL you want to shorten

    📝 *Note:* Your API key will be stored securely for future use.

    If you encounter any issues, please contact support.
    """
    update.message.reply_text(help_message, parse_mode='Markdown')

# URL shortening logic
def shorten_url(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Please enter your API key:")
    return 'API_KEY'

def get_api_key(update: Update, context: CallbackContext) -> None:
    user_api_key = update.message.text
    context.user_data['api_key'] = user_api_key
    update.message.reply_text("Please enter the URL you want to shorten:")
    return 'URL'

def get_url(update: Update, context: CallbackContext) -> None:
    url_to_shorten = update.message.text
    api_key = context.user_data.get('api_key')
    shortened_url = shorten_url_with_api(api_key, url_to_shorten)
    if shortened_url:
        update.message.reply_text(f"✅ *Shortened URL:* {shortened_url}", parse_mode='Markdown')
    else:
        update.message.reply_text("❌ *Error:* Unable to shorten the URL. Please check your API key and try again.", parse_mode='Markdown')
    return -1

def shorten_url_with_api(api_key: str, url: str) -> str:
    api_url = f"https://blog.thunderlinks.site/api?api={api_key}&url={url}"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            return data.get('shortenedUrl')
    return None

# Cancel command
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

# Conversation handler
URL_SHORTENER_CONVERSATION = ConversationHandler(
    entry_points=[CommandHandler('shorten', shorten_url)],
    states={
        'API_KEY': [MessageHandler(Filters.text & ~Filters.command, get_api_key)],
        'URL': [MessageHandler(Filters.text & ~Filters.command, get_url)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

# Main function
def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(URL_SHORTENER_CONVERSATION)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
