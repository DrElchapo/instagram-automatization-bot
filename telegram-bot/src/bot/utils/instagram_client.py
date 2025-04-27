from typing import List, Optional, Dict
from instagrapi import Client
from instagrapi.exceptions import (
    ClientError,
    ClientUnauthorizedError,
    ClientThrottledError,
    ClientConnectionError
)
import time
from datetime import datetime, timedelta
from config.config import RATE_LIMITS, MAX_RETRIES, RETRY_DELAY

class InstagramClient:
    def __init__(self, access_token: str):
        self.client = Client()
        self.access_token = access_token
        self._rate_limits = {
            'likes': {'count': 0, 'reset_time': datetime.now()},
            'comments': {'count': 0, 'reset_time': datetime.now()},
            'follows': {'count': 0, 'reset_time': datetime.now()},
            'dms': {'count': 0, 'reset_time': datetime.now()}
        }

    def _check_rate_limit(self, action: str) -> bool:
        """Check if rate limit for an action has been reached"""
        limit = self._rate_limits[action]
        if datetime.now() >= limit['reset_time']:
            limit['count'] = 0
            limit['reset_time'] = datetime.now() + timedelta(hours=1)
            return True
        
        if limit['count'] >= RATE_LIMITS[f'{action}_per_hour']:
            return False
        
        limit['count'] += 1
        return True

    def _handle_retry(self, func, *args, **kwargs):
        """Handle retries for Instagram actions"""
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except (ClientError, ClientUnauthorizedError, ClientConnectionError) as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(RETRY_DELAY)
            except ClientThrottledError:
                time.sleep(60)  # Wait a minute if throttled

    def like_post(self, media_id: str) -> bool:
        """Like a post"""
        if not self._check_rate_limit('likes'):
            raise Exception("Rate limit reached for likes")
        return self._handle_retry(self.client.media_like, media_id)

    def comment_post(self, media_id: str, text: str) -> bool:
        """Comment on a post"""
        if not self._check_rate_limit('comments'):
            raise Exception("Rate limit reached for comments")
        return self._handle_retry(self.client.media_comment, media_id, text)

    def follow_user(self, user_id: str) -> bool:
        """Follow a user"""
        if not self._check_rate_limit('follows'):
            raise Exception("Rate limit reached for follows")
        return self._handle_retry(self.client.user_follow, user_id)

    def send_dm(self, user_id: str, text: str) -> bool:
        """Send direct message"""
        if not self._check_rate_limit('dms'):
            raise Exception("Rate limit reached for DMs")
        return self._handle_retry(self.client.direct_send, text, user_ids=[user_id])

    def get_user_id(self, username: str) -> str:
        """Get user ID from username"""
        return self._handle_retry(self.client.user_id_from_username, username)

    def get_media_id(self, shortcode: str) -> str:
        """Get media ID from shortcode"""
        return self._handle_retry(self.client.media_id_from_shortcode, shortcode)

    def search_hashtag(self, hashtag: str, amount: int = 10) -> List[Dict]:
        """Search posts by hashtag"""
        return self._handle_retry(
            self.client.hashtag_medias_recent,
            hashtag,
            amount=amount
        )

    def get_user_followers(self, user_id: str, amount: int = 10) -> List[Dict]:
        """Get user followers"""
        return self._handle_retry(
            self.client.user_followers,
            user_id,
            amount=amount
        )

    def get_user_following(self, user_id: str, amount: int = 10) -> List[Dict]:
        """Get users that a user is following"""
        return self._handle_retry(
            self.client.user_following,
            user_id,
            amount=amount
        )

    def get_user_medias(self, user_id: str, amount: int = 10) -> List[Dict]:
        """Get user's media posts"""
        return self._handle_retry(
            self.client.user_medias,
            user_id,
            amount=amount
        ) 