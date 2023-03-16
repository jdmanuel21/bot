import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import os
import requests
import uuid
import urllib.request
import tqdm
import telegram

bot_token = '6287740609:AAEolD1PgPf4cEzpf4ujroOqlFf21_zlE9s'

webhook_url = 'https://bot-jdmanuel21.koyeb.app/'

# Create a bot instance using the provided token

bot = telegram.Bot(token=bot_token)

# Set the webhook URL for the bot

bot.setWebhook(url=webhook_url)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! Use /savevideo to save a video')

def save_video(update, context):
    """Save a video sent by the user and prompt for a caption and channel ID."""
    update.message.reply_text('Please send the video you want to save.')
    return 'GET_VIDEO'

def get_video(update, context):
    """Handle the video sent by the user or from a URL and prompt for a caption and channel ID."""
    # Check if the message contains a video file
    if update.message.video is not None:
        # Get the video file from the user's message
        video_file = update.message.video.get_file()

        # Generate a unique filename using UUID
        filename = str(uuid.uuid4()) + '.mp4'

        # Download the video from Telegram's servers to local filesystem
        download_video_from_url(video_file.file_path, filename)

        # Store the video filename in the user's context
        context.user_data['filename'] = filename

        # Prompt the user for a caption and channel ID
        update.message.reply_text('Got it! Please enter a caption for the video.')
        return 'GET_CAPTION'
    else:
        # Check if the message contains a video URL
        if update.message.text.startswith('http'):
            # Download the video from the URL and save it to a local file
            url = update.message.text
            filename = str(uuid.uuid4()) + '.mp4'
            download_video_from_url(url, filename)
            
            # Store the video filename in the user's context
            context.user_data['filename'] = filename
            
            # Prompt the user for a caption and channel ID
            update.message.reply_text('Got it! Please enter a caption for the video.')
            return 'GET_CAPTION'
        
        # If neither a video file nor a video URL was provided, notify the user and end the conversation
        update.message.reply_text('Sorry, I didn\'t understand. Please send a video file or a video URL.')
        return ConversationHandler.END

def get_caption(update, context):
    """Handle the video caption and channel ID sent by the user and prompt for a channel ID."""
    # Store the caption in the user's context
    context.user_data['caption'] = update.message.text
    
    # Prompt the user for a channel ID
    update.message.reply_text('Please enter the ID of the channel you want to post the video to.')
    return 'GET_CHANNEL_ID'

def get_channel_id(update, context):
    """Handle the channel ID sent by the user and upload the video to the channel."""
    # Store the channel ID in the user's context
    context.user_data['channel_id'] = update.message.text
    
    # Get the video filename from the user's context
    filename = context.user_data['filename']
    
    # Upload the video to the Telegram channel
    try:
        upload_video_to_channel(filename, context.user_data['caption'], context.user_data['channel_id'])
    except Exception as e:
        logger.error(f'Failed to upload video: {e}')
        update.message.reply_text('Sorry, there was an error uploading your video. Please try again later.')
        os.remove(filename)
        return ConversationHandler.END
    
    # Remove the video file from the local filesystem
    os.remove(filename)
    
    # Clear the user's context
    context.user_data.clear()
    
    # Send a confirmation message to the user
    update.message.reply_text('Your video has been saved!')
    return ConversationHandler.END

def cancel(update, context):
    """Cancel the current conversation and clear the user's context."""
    update.message.reply_text('Conversation cancelled.')
    context.user_data.clear()
    return ConversationHandler.END

def download_video_from_url(url, filename):
    """Download a video from a URL and save it to the local filesystem."""
    response = requests.get(url, stream=True)
    
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024
    progress_bar = tqdm.tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    
    with open(filename, 'wb') as f:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            f.write(data)
            
    progress_bar.close()

def upload_video_to_channel(filename, caption, channel_id):
    """Upload a video to a Telegram channel."""
    telegram_token = os.environ['6287740609:AAEolD1PgPf4cEzpf4ujroOqlFf21_zlE9s']
    bot = telegram.Bot(token=telegram_token)
    
    # Open the video file
    with open(filename, 'rb') as f:
        # Upload the video to the Telegram servers
        message = bot.send_video(chat_id=channel_id, video=f, caption=caption)
        
    return message
