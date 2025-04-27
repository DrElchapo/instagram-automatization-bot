from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient
from config.config import MONGODB_URI, DATABASE_NAME

class User:
    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id
        self.instagram_username: Optional[str] = None
        self.instagram_access_token: Optional[str] = None
        self.instagram_refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.is_active: bool = False
        self.settings: Dict = {
            'auto_like': False,
            'auto_comment': False,
            'auto_follow': False,
            'auto_dm': False,
            'hashtags': [],
            'target_users': [],
            'comment_templates': [],
            'dm_templates': []
        }
        self.stats: Dict = {
            'likes_sent': 0,
            'comments_sent': 0,
            'follows_sent': 0,
            'dms_sent': 0,
            'last_activity': None
        }
        self._db = MongoClient(MONGODB_URI)[DATABASE_NAME]

    def save(self) -> None:
        """Save user data to database"""
        self._db.users.update_one(
            {'telegram_id': self.telegram_id},
            {
                '$set': {
                    'instagram_username': self.instagram_username,
                    'instagram_access_token': self.instagram_access_token,
                    'instagram_refresh_token': self.instagram_refresh_token,
                    'token_expires_at': self.token_expires_at,
                    'is_active': self.is_active,
                    'settings': self.settings,
                    'stats': self.stats
                }
            },
            upsert=True
        )

    @classmethod
    def get_by_telegram_id(cls, telegram_id: int) -> Optional['User']:
        """Retrieve user by Telegram ID"""
        db = MongoClient(MONGODB_URI)[DATABASE_NAME]
        user_data = db.users.find_one({'telegram_id': telegram_id})
        if user_data:
            user = cls(telegram_id)
            user.instagram_username = user_data.get('instagram_username')
            user.instagram_access_token = user_data.get('instagram_access_token')
            user.instagram_refresh_token = user_data.get('instagram_refresh_token')
            user.token_expires_at = user_data.get('token_expires_at')
            user.is_active = user_data.get('is_active', False)
            user.settings = user_data.get('settings', {})
            user.stats = user_data.get('stats', {})
            return user
        return None

    def update_settings(self, settings: Dict) -> None:
        """Update user settings"""
        self.settings.update(settings)
        self.save()

    def update_stats(self, action: str, count: int = 1) -> None:
        """Update user statistics"""
        if action in self.stats:
            self.stats[action] += count
            self.stats['last_activity'] = datetime.now()
            self.save()

    def is_token_valid(self) -> bool:
        """Check if Instagram access token is valid"""
        if not self.token_expires_at:
            return False
        return datetime.now() < self.token_expires_at

    def get_activity_report(self) -> str:
        """Generate activity report"""
        return (
            f"📊 Activity Report for {self.instagram_username or 'User'}\n\n"
            f"❤️ Likes sent: {self.stats['likes_sent']}\n"
            f"💬 Comments sent: {self.stats['comments_sent']}\n"
            f"👥 Follows sent: {self.stats['follows_sent']}\n"
            f"📨 DMs sent: {self.stats['dms_sent']}\n"
            f"⏰ Last activity: {self.stats['last_activity'] or 'Never'}"
        ) 