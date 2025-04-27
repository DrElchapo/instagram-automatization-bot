from telegram import Update
from telegram.ext import ContextTypes
from typing import Dict, List
import asyncio
from datetime import datetime
from models.user import User
from bot.utils.instagram_client import InstagramClient
from config.config import DEFAULT_SCHEDULE

class InstagramActionHandler:
    def __init__(self):
        self.active_tasks: Dict[int, Dict[str, asyncio.Task]] = {}

    async def start_likes(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start auto-liking posts"""
        user = User.get_by_telegram_id(update.effective_user.id)
        if not user or not user.is_token_valid():
            await update.message.reply_text("Please authenticate with Instagram first using /auth")
            return

        if 'likes' in self.active_tasks.get(user.telegram_id, {}):
            await update.message.reply_text("Auto-liking is already active")
            return

        instagram_client = InstagramClient(user.instagram_access_token)
        task = asyncio.create_task(self._auto_like_loop(user, instagram_client))
        
        if user.telegram_id not in self.active_tasks:
            self.active_tasks[user.telegram_id] = {}
        self.active_tasks[user.telegram_id]['likes'] = task

        await update.message.reply_text("Auto-liking started! Use /stop_likes to stop")

    async def stop_likes(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Stop auto-liking posts"""
        user = User.get_by_telegram_id(update.effective_user.id)
        if not user:
            return

        if 'likes' in self.active_tasks.get(user.telegram_id, {}):
            self.active_tasks[user.telegram_id]['likes'].cancel()
            del self.active_tasks[user.telegram_id]['likes']
            await update.message.reply_text("Auto-liking stopped")

    async def _auto_like_loop(self, user: User, instagram_client: InstagramClient) -> None:
        """Background task for auto-liking posts"""
        while True:
            try:
                for hashtag in user.settings['hashtags']:
                    posts = instagram_client.search_hashtag(hashtag)
                    for post in posts:
                        if instagram_client.like_post(post['id']):
                            user.update_stats('likes_sent')
                await asyncio.sleep(DEFAULT_SCHEDULE['likes']['interval'] * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                await asyncio.sleep(60)  # Wait a minute on error

    async def start_comments(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start auto-commenting on posts"""
        user = User.get_by_telegram_id(update.effective_user.id)
        if not user or not user.is_token_valid():
            await update.message.reply_text("Please authenticate with Instagram first using /auth")
            return

        if 'comments' in self.active_tasks.get(user.telegram_id, {}):
            await update.message.reply_text("Auto-commenting is already active")
            return

        instagram_client = InstagramClient(user.instagram_access_token)
        task = asyncio.create_task(self._auto_comment_loop(user, instagram_client))
        
        if user.telegram_id not in self.active_tasks:
            self.active_tasks[user.telegram_id] = {}
        self.active_tasks[user.telegram_id]['comments'] = task

        await update.message.reply_text("Auto-commenting started! Use /stop_comments to stop")

    async def stop_comments(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Stop auto-commenting on posts"""
        user = User.get_by_telegram_id(update.effective_user.id)
        if not user:
            return

        if 'comments' in self.active_tasks.get(user.telegram_id, {}):
            self.active_tasks[user.telegram_id]['comments'].cancel()
            del self.active_tasks[user.telegram_id]['comments']
            await update.message.reply_text("Auto-commenting stopped")

    async def _auto_comment_loop(self, user: User, instagram_client: InstagramClient) -> None:
        """Background task for auto-commenting on posts"""
        while True:
            try:
                for hashtag in user.settings['hashtags']:
                    posts = instagram_client.search_hashtag(hashtag)
                    for post in posts:
                        for template in user.settings['comment_templates']:
                            if instagram_client.comment_post(post['id'], template):
                                user.update_stats('comments_sent')
                await asyncio.sleep(DEFAULT_SCHEDULE['comments']['interval'] * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                await asyncio.sleep(60)

    async def start_follow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start auto-following users"""
        user = User.get_by_telegram_id(update.effective_user.id)
        if not user or not user.is_token_valid():
            await update.message.reply_text("Please authenticate with Instagram first using /auth")
            return

        if 'follows' in self.active_tasks.get(user.telegram_id, {}):
            await update.message.reply_text("Auto-following is already active")
            return

        instagram_client = InstagramClient(user.instagram_access_token)
        task = asyncio.create_task(self._auto_follow_loop(user, instagram_client))
        
        if user.telegram_id not in self.active_tasks:
            self.active_tasks[user.telegram_id] = {}
        self.active_tasks[user.telegram_id]['follows'] = task

        await update.message.reply_text("Auto-following started! Use /stop_follow to stop")

    async def stop_follow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Stop auto-following users"""
        user = User.get_by_telegram_id(update.effective_user.id)
        if not user:
            return

        if 'follows' in self.active_tasks.get(user.telegram_id, {}):
            self.active_tasks[user.telegram_id]['follows'].cancel()
            del self.active_tasks[user.telegram_id]['follows']
            await update.message.reply_text("Auto-following stopped")

    async def _auto_follow_loop(self, user: User, instagram_client: InstagramClient) -> None:
        """Background task for auto-following users"""
        while True:
            try:
                for target_user in user.settings['target_users']:
                    user_id = instagram_client.get_user_id(target_user)
                    followers = instagram_client.get_user_followers(user_id)
                    for follower in followers:
                        if instagram_client.follow_user(follower['id']):
                            user.update_stats('follows_sent')
                await asyncio.sleep(DEFAULT_SCHEDULE['follows']['interval'] * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                await asyncio.sleep(60)

    async def get_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Get activity report"""
        user = User.get_by_telegram_id(update.effective_user.id)
        if not user:
            await update.message.reply_text("Please authenticate with Instagram first using /auth")
            return

        report = user.get_activity_report()
        await update.message.reply_text(report) 