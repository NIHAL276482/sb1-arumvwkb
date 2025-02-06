# Telegram Snipe Bot

A Telegram bot that tracks and retrieves deleted messages.

## Features

- `/snipe` - Shows the last deleted message in the group (admin only)
- `/godsnipe` - Shows all deleted messages (owner only)
- Tracks messages deleted within the last 24 hours
- Includes timestamps and usernames
- Advanced error handling
- Owner-only commands

## Setup

1. Create a new bot using [@BotFather](https://t.me/botfather) on Telegram
2. Get your bot token
3. Replace `'YOUR_BOT_TOKEN'` in `bot.py` with your actual bot token
4. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the bot:
   ```bash
   python bot.py
   ```

## Hosting on PythonAnywhere

1. Upload both `bot.py` and `requirements.txt` to your PythonAnywhere account
2. Install the requirements using pip
3. Set up a new Web App or use the Always-on task feature
4. Start the bot using `python bot.py`

## Security Features

- Only group admins can use `/snipe`
- Only the owner (chat ID: 7187126565) can use `/godsnipe`
- Message tracking with timestamps
- Error handling and logging