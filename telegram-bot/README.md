# Instagram Automation Telegram Bot

A Telegram bot that allows users to automate various Instagram actions such as liking posts, commenting, following users, and sending direct messages.

## Features

- Instagram OAuth authentication
- Automated actions:
  - Auto-liking posts based on hashtags
  - Auto-commenting with customizable templates
  - Auto-following users
  - Sending direct messages
- User-friendly Telegram interface
- Activity tracking and reporting
- Rate limiting to prevent Instagram blocks
- Configurable settings for each user

## Prerequisites

- Python 3.8 or higher
- MongoDB database
- Instagram Developer Account
- Telegram Bot Token (from @BotFather)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/instagram-telegram-bot.git
cd instagram-telegram-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
INSTAGRAM_CLIENT_ID=your_instagram_client_id
INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
INSTAGRAM_REDIRECT_URI=your_redirect_uri
MONGODB_URI=your_mongodb_uri
DATABASE_NAME=instagram_bot
LOG_LEVEL=INFO
LOG_FILE=bot.log
```

## Usage

1. Start the bot:
```bash
python src/bot/main.py
```

2. Open Telegram and start a conversation with your bot.

3. Use the following commands:
- `/start` - Start the bot and see available options
- `/auth` - Authenticate with Instagram
- `/start_likes` - Start auto-liking posts
- `/stop_likes` - Stop auto-liking
- `/start_comments` - Start auto-commenting
- `/stop_comments` - Stop auto-commenting
- `/start_follow` - Start auto-following
- `/stop_follow` - Stop auto-following
- `/get_report` - Get activity report

## Configuration

After authentication, you can configure the following settings:
- Hashtags to target
- Target users to follow
- Comment templates
- DM templates

## Rate Limits

The bot implements rate limiting to prevent Instagram blocks:
- Likes: 30 per hour
- Comments: 20 per hour
- Follows: 20 per hour
- DMs: 10 per hour

## Error Handling

The bot includes comprehensive error handling for:
- Authentication failures
- Rate limit exceeded
- Network issues
- Instagram API errors

## Security

- All user data is stored securely in MongoDB
- Instagram access tokens are encrypted
- Rate limiting prevents abuse
- User sessions are isolated

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This bot is for educational purposes only. Please use it responsibly and in accordance with Instagram's Terms of Service. The developers are not responsible for any misuse or violations of Instagram's policies.
