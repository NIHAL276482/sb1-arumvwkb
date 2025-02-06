from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from datetime import datetime, timedelta
import json
from typing import Dict, List

# Store deleted messages
deleted_messages: Dict[str, List[Dict]] = {}
OWNER_ID = 7187126565  # Your Telegram chat ID

async def store_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Store message data when a message is sent"""
    if not update.message or not update.message.text:
        return

    chat_id = str(update.message.chat_id)
    if chat_id not in deleted_messages:
        deleted_messages[chat_id] = []

    # Clean up old messages (older than 24 hours)
    now = datetime.now()
    deleted_messages[chat_id] = [
        msg for msg in deleted_messages[chat_id]
        if (now - datetime.fromisoformat(msg['timestamp'])) <= timedelta(hours=24)
    ]

    message_data = {
        'message_id': update.message.message_id,
        'user_id': update.message.from_user.id,
        'username': update.message.from_user.username or update.message.from_user.first_name,
        'text': update.message.text,
        'timestamp': datetime.now().isoformat(),
        'deleted': False
    }
    
    deleted_messages[chat_id].append(message_data)

async def on_message_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Track when a message is deleted"""
    if not update.message:
        return
        
    chat_id = str(update.message.chat_id)
    if chat_id in deleted_messages:
        # Mark messages as deleted
        for msg in deleted_messages[chat_id]:
            if msg['message_id'] == update.message.message_id:
                msg['deleted'] = True
                msg['delete_time'] = datetime.now().isoformat()
                break

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command"""
    if not update.message:
        return

    welcome_text = (
        "👋 Hello! I'm a message tracking bot.\n\n"
        "Available commands:\n"
        "/snipe - Show last deleted message (admin only)\n"
        "/godsnipe - Show all deleted messages (owner only)\n\n"
        "Add me to your group and make me admin to start tracking messages!"
    )
    await update.message.reply_text(welcome_text)

async def snipe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the last deleted message (only for admins)"""
    try:
        if not update.message:
            return

        chat_id = str(update.message.chat_id)
        user_id = update.message.from_user.id
        
        # Check if user is admin
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        if not chat_member.status in ['administrator', 'creator'] and user_id != OWNER_ID:
            await update.message.reply_text("❌ Only administrators can use this command.")
            return

        if chat_id not in deleted_messages:
            await update.message.reply_text("No deleted messages found.")
            return

        # Get messages deleted in the last 24 hours
        now = datetime.now()
        recent_deleted = [
            msg for msg in deleted_messages[chat_id]
            if msg['deleted'] and 
            (now - datetime.fromisoformat(msg['timestamp'])) <= timedelta(hours=24)
        ]

        if not recent_deleted:
            await update.message.reply_text("No recently deleted messages found.")
            return

        # Get the most recent deleted message
        last_deleted = recent_deleted[-1]
        response = (
            f"🗑 Deleted Message Found:\n\n"
            f"From: @{last_deleted['username']}\n"
            f"Sent: {datetime.fromisoformat(last_deleted['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Deleted: {datetime.fromisoformat(last_deleted.get('delete_time', last_deleted['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Message: {last_deleted['text']}\n\n"
            f"Requested by: @{update.message.from_user.username or update.message.from_user.first_name}"
        )
        
        await update.message.reply_text(response)
    except Exception as e:
        print(f"Error in snipe command: {e}")
        await update.message.reply_text("❌ An error occurred while retrieving the deleted message.")

async def godsnipe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all deleted messages (only for owner)"""
    try:
        if not update.message or update.message.from_user.id != OWNER_ID:
            await update.message.reply_text("❌ This command is only for the bot owner.")
            return

        chat_id = str(update.message.chat_id)
        if chat_id not in deleted_messages:
            await update.message.reply_text("No deleted messages found.")
            return

        # Get messages deleted in the last 24 hours
        now = datetime.now()
        deleted = [
            msg for msg in deleted_messages[chat_id]
            if msg['deleted'] and 
            (now - datetime.fromisoformat(msg['timestamp'])) <= timedelta(hours=24)
        ]

        if not deleted:
            await update.message.reply_text("No deleted messages found.")
            return

        response = "🗑 All Deleted Messages:\n\n"
        for msg in deleted:
            response += (
                f"From: @{msg['username']}\n"
                f"Sent: {datetime.fromisoformat(msg['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Deleted: {datetime.fromisoformat(msg.get('delete_time', msg['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Message: {msg['text']}\n"
                f"{'=' * 30}\n"
            )

        # Split long messages if needed
        if len(response) > 4000:
            chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(response)
    except Exception as e:
        print(f"Error in godsnipe command: {e}")
        await update.message.reply_text("❌ An error occurred while retrieving deleted messages.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    print(f"Error occurred: {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "❌ An error occurred while processing your request. Please try again later."
        )

def main() -> None:
    """Start the bot"""
    try:
        # Replace 'YOUR_BOT_TOKEN' with your actual bot token from BotFather
        application = Application.builder().token('YOUR_BOT_TOKEN').build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("snipe", snipe))
        application.add_handler(CommandHandler("godsnipe", godsnipe))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, store_message))
        application.add_handler(MessageHandler(filters.StatusUpdate.MESSAGE_DELETE, on_message_delete))
        application.add_error_handler(error_handler)

        # Start the bot
        print("Bot is running...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == '__main__':
    main()