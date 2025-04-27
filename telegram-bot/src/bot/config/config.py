import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ADMIN_IDS = [int(id) for id in os.getenv('TELEGRAM_ADMIN_IDS', '').split(',') if id]

# Instagram Configuration
INSTAGRAM_CLIENT_ID = os.getenv('INSTAGRAM_CLIENT_ID')
INSTAGRAM_CLIENT_SECRET = os.getenv('INSTAGRAM_CLIENT_SECRET')
INSTAGRAM_REDIRECT_URI = os.getenv('INSTAGRAM_REDIRECT_URI')

# Database Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'instagram_bot')

# Rate Limiting Configuration
RATE_LIMITS = {
    'likes_per_hour': 30,
    'comments_per_hour': 20,
    'follows_per_hour': 20,
    'dms_per_hour': 10
}

# Task Scheduling Configuration
DEFAULT_SCHEDULE = {
    'likes': {'interval': 60, 'unit': 'minutes'},
    'comments': {'interval': 30, 'unit': 'minutes'},
    'follows': {'interval': 60, 'unit': 'minutes'},
    'dms': {'interval': 120, 'unit': 'minutes'}
}

# Error Handling Configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log') 