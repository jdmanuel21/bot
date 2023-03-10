import os

import logging

from telegram import ChatAction

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Set up logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize the Telegram bot with your bot token

TOKEN = "6287740609:AAGSsav-HegxRJbAoV2jVCzhkn2z8Tb6Kcg"

updater = Updater(token=TOKEN, use_context=True)

dispatcher = updater.dispatcher

# Define a function to handle the /start command

def start(update, context):

    context.bot.send_message(chat_id=update.message.chat_id, text="Hi, I'm your video downloader and uploader bot. Send me a video to download and upload to a channel or group.")

# Define a function to handle new messages in the Telegram channel or group

def save_video(update, context):

    message = update.message

    chat_id = message.chat_id

    video = message.video

    video_file = context.bot.get_file(video.file_id)

    filename = "{}.mp4".format(video.file_id)

    video_file.download(filename, progress=progress_callback)

    context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_VIDEO)

    caption = "Downloaded using @YourBotUsername"

    if "caption" in context.user_data:

        caption = context.user_data["caption"]

    context.bot.send_video(chat_id=context.user_data["target_id"], video=open(filename, "rb"), caption=caption)

    context.bot.send_message(chat_id=chat_id, text="Video saved and uploaded successfully!")

# Define a function to handle errors

def error(update, context):

    logging.error('Error: %s', context.error)

# Define a function to handle progress updates during file downloads

def progress_callback(current, total):

    percentage = round(current/total*100, 2)

    print("Downloaded {} of {} bytes ({}% complete)...".format(current, total, percentage))

# Define a function to handle the /target command

def set_target(update, context):

    target_id = update.message.text.split()[1]

    if not target_id.isdigit():

        context.bot.send_message(chat_id=update.message.chat_id, text="Invalid ID. Please enter a valid numeric ID.")

    else:

        context.user_data["target_id"] = int(target_id)

        context.bot.send_message(chat_id=update.message.chat_id, text="Target ID set to {}.".format(target_id))

# Define a function to handle the /caption command

def set_caption(update, context):

    caption = update.message.text.split(maxsplit=1)[1]

    context.user_data["caption"] = caption

    context.bot.send_message(chat_id=update.message.chat_id, text="Caption set to: {}".format(caption))

# Set up message handlers to listen for commands and new messages containing videos

dispatcher.add_handler(CommandHandler('start', start))

dispatcher.add_handler(CommandHandler('target', set_target))

dispatcher.add_handler(CommandHandler('caption', set_caption))

dispatcher.add_handler(MessageHandler(Filters.video, save_video))

dispatcher.add_error_handler(error)

# Start the Telegram bot

updater.start_polling()

