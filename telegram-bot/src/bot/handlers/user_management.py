from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from typing import Dict, List
import requests
from datetime import datetime, timedelta
from models.user import User
from config.config import (
    INSTAGRAM_CLIENT_ID,
    INSTAGRAM_CLIENT_SECRET,
    INSTAGRAM_REDIRECT_URI
)

# Conversation states
AUTH, SETTINGS = range(2)

class UserManagementHandler:
    def __init__(self):
        self.auth_states: Dict[int, str] = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start command handler"""
        user = User.get_by_telegram_id(update.effective_user.id)
        if not user:
            user = User(update.effective_user.id)
            user.save()

        keyboard = [
            [InlineKeyboardButton("Authenticate Instagram", callback_data='auth')],
            [InlineKeyboardButton("Configure Settings", callback_data='settings')],
            [InlineKeyboardButton("Get Report", callback_data='report')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Welcome to Instagram Automation Bot! Choose an option:",
            reply_markup=reply_markup
        )

    async def auth_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle authentication callback"""
        query = update.callback_query
        await query.answer()

        if query.data == 'auth':
            auth_url = (
                f"https://api.instagram.com/oauth/authorize"
                f"?client_id={INSTAGRAM_CLIENT_ID}"
                f"&redirect_uri={INSTAGRAM_REDIRECT_URI}"
                f"&scope=user_profile,user_media"
                f"&response_type=code"
            )
            self.auth_states[query.from_user.id] = 'waiting_code'
            await query.message.reply_text(
                f"Please authenticate with Instagram by visiting this URL:\n{auth_url}\n"
                "After authentication, send me the code you receive."
            )
            return AUTH

    async def handle_auth_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle Instagram OAuth code"""
        if update.effective_user.id not in self.auth_states:
            await update.message.reply_text("Please start the authentication process using /start")
            return ConversationHandler.END

        code = update.message.text
        try:
            # Exchange code for access token
            response = requests.post(
                "https://api.instagram.com/oauth/access_token",
                data={
                    'client_id': INSTAGRAM_CLIENT_ID,
                    'client_secret': INSTAGRAM_CLIENT_SECRET,
                    'grant_type': 'authorization_code',
                    'redirect_uri': INSTAGRAM_REDIRECT_URI,
                    'code': code
                }
            )
            data = response.json()

            if 'access_token' in data:
                user = User.get_by_telegram_id(update.effective_user.id)
                user.instagram_access_token = data['access_token']
                user.token_expires_at = datetime.now() + timedelta(days=60)
                user.is_active = True
                user.save()

                del self.auth_states[update.effective_user.id]
                await update.message.reply_text(
                    "Successfully authenticated with Instagram! "
                    "You can now use automation features."
                )
                return ConversationHandler.END
            else:
                await update.message.reply_text(
                    "Authentication failed. Please try again using /start"
                )
                return ConversationHandler.END

        except Exception as e:
            await update.message.reply_text(
                "An error occurred during authentication. Please try again using /start"
            )
            return ConversationHandler.END

    async def settings_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle settings callback"""
        query = update.callback_query
        await query.answer()

        if query.data == 'settings':
            user = User.get_by_telegram_id(query.from_user.id)
            if not user or not user.is_token_valid():
                await query.message.reply_text("Please authenticate with Instagram first")
                return

            keyboard = [
                [InlineKeyboardButton("Set Hashtags", callback_data='set_hashtags')],
                [InlineKeyboardButton("Set Target Users", callback_data='set_target_users')],
                [InlineKeyboardButton("Set Comment Templates", callback_data='set_comments')],
                [InlineKeyboardButton("Set DM Templates", callback_data='set_dms')],
                [InlineKeyboardButton("Back", callback_data='back')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.message.reply_text(
                "Configure your automation settings:",
                reply_markup=reply_markup
            )
            return SETTINGS

    async def handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle settings updates"""
        query = update.callback_query
        await query.answer()

        user = User.get_by_telegram_id(query.from_user.id)
        if not user:
            return

        if query.data == 'set_hashtags':
            await query.message.reply_text(
                "Send hashtags separated by spaces (e.g., #travel #photography):"
            )
            context.user_data['setting_type'] = 'hashtags'
        elif query.data == 'set_target_users':
            await query.message.reply_text(
                "Send target usernames separated by spaces (e.g., user1 user2):"
            )
            context.user_data['setting_type'] = 'target_users'
        elif query.data == 'set_comments':
            await query.message.reply_text(
                "Send comment templates, one per line:"
            )
            context.user_data['setting_type'] = 'comment_templates'
        elif query.data == 'set_dms':
            await query.message.reply_text(
                "Send DM templates, one per line:"
            )
            context.user_data['setting_type'] = 'dm_templates'
        elif query.data == 'back':
            await self.start(update, context)
            return ConversationHandler.END

    async def update_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Update user settings based on input"""
        setting_type = context.user_data.get('setting_type')
        if not setting_type:
            return

        user = User.get_by_telegram_id(update.effective_user.id)
        if not user:
            return

        if setting_type in ['hashtags', 'target_users']:
            values = update.message.text.split()
        else:
            values = update.message.text.split('\n')

        user.settings[setting_type] = values
        user.save()

        await update.message.reply_text(
            f"Successfully updated {setting_type.replace('_', ' ')}!"
        )
        return ConversationHandler.END 