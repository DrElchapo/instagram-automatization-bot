import asyncio
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler
)
from config.config import TELEGRAM_BOT_TOKEN, LOG_LEVEL, LOG_FILE
from bot.handlers.instagram_actions import InstagramActionHandler
from bot.handlers.user_management import UserManagementHandler, AUTH, SETTINGS

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL),
    filename=LOG_FILE
)
logger = logging.getLogger(__name__)

class InstagramBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.instagram_handler = InstagramActionHandler()
        self.user_handler = UserManagementHandler()

    def setup_handlers(self):
        # Start command
        self.application.add_handler(CommandHandler("start", self.user_handler.start))

        # Authentication conversation handler
        auth_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.user_handler.auth_callback, pattern='^auth$')],
            states={
                AUTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.user_handler.handle_auth_code)]
            },
            fallbacks=[CommandHandler("start", self.user_handler.start)]
        )
        self.application.add_handler(auth_handler)

        # Settings conversation handler
        settings_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.user_handler.settings_callback, pattern='^settings$')],
            states={
                SETTINGS: [
                    CallbackQueryHandler(self.user_handler.handle_settings),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.user_handler.update_settings)
                ]
            },
            fallbacks=[CommandHandler("start", self.user_handler.start)]
        )
        self.application.add_handler(settings_handler)

        # Instagram action commands
        self.application.add_handler(CommandHandler("start_likes", self.instagram_handler.start_likes))
        self.application.add_handler(CommandHandler("stop_likes", self.instagram_handler.stop_likes))
        self.application.add_handler(CommandHandler("start_comments", self.instagram_handler.start_comments))
        self.application.add_handler(CommandHandler("stop_comments", self.instagram_handler.stop_comments))
        self.application.add_handler(CommandHandler("start_follow", self.instagram_handler.start_follow))
        self.application.add_handler(CommandHandler("stop_follow", self.instagram_handler.stop_follow))
        self.application.add_handler(CommandHandler("get_report", self.instagram_handler.get_report))

        # Error handler
        self.application.add_error_handler(self.error_handler)

    async def error_handler(self, update, context):
        """Handle errors in the bot"""
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "An error occurred. Please try again later."
            )

    def run(self):
        """Run the bot"""
        self.setup_handlers()
        self.application.run_polling()

def main():
    bot = InstagramBot()
    bot.run()

if __name__ == '__main__':
    main() 