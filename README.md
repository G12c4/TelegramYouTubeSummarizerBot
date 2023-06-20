# TelegramYouTubeSummarizerBot
The Telegram YouTube Summarizer Bot is a tool designed to send summarized content of YouTube videos directly to your telegram groups or channels

# Setup Guide for the Video Processing Telegram Bot

This guide will provide you with the instructions to set up the Video Processing Telegram Bot. Please follow these steps carefully.

## Prerequisites

Before starting, make sure you have Python installed on your system.

## 1. Set up a YouTube API key

The bot needs access to the YouTube API to fetch the latest videos from specific channels.

1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project, or select an existing one.
3. Enable the YouTube Data API v3 on your project by navigating to `APIs & Services -> Library -> YouTube Data API v3`.
4. Navigate to `APIs & Services -> Credentials` and click on `CREATE CREDENTIALS -> API key`.
5. Copy the generated API key.

In the config.py script, replace `YOUR_YOUTUBE_API_KEY` with your generated API key.

## 2. Define your YouTube channel IDs

To filter videos from specific channels, you need to provide the IDs of these channels. 

Replace `channel_id1`, `channel_id2`, etc. in the `CHANNEL_IDS` list with the IDs of the channels you are interested in.

## 3. Set up a Telegram bot

The bot will send the key takeaways to a specific Telegram channel.

1. Create a new bot using the BotFather on Telegram. Follow the instructions provided by the BotFather to get your bot token.
2. Copy the bot token.

In the config.py script, replace `YOUR_BOT_TOKEN` with your bot token.

## 4. Define your Telegram channel ID

You need to provide the ID of the Telegram channel where the bot will send the messages.

https://neliosoftware.com/content/help/how-do-i-get-the-channel-id-in-telegram/

Replace `YOUR_TELEGRAM_CHANNEL_ID` with the ID of your Telegram channel.

## 5. Set up an OpenAI API key

The bot uses OpenAI's GPT-3.5-turbo-16k to generate key takeaways from the video descriptions.

1. Navigate to the [OpenAI website](https://www.openai.com/).
2. Create a new API key.
3. Copy the generated API key.

In the config.py script, replace `YOUR_OPENAI_API_KEY` with your generated API key.

## 6. Define the storage file

The bot uses a txt file to store the IDs of the processed videos.

Replace `video_store.json` in `STORE_FILE` with the path to your txt file. If the file does not exist, the bot will create it.

Once you have made these modifications, you should be ready to run the Python script.

python main.py

## 7. Now, set these variables in the config.py file

### Youtube
YOUTUBE_API_SERVICE_NAME = 'youtube' <br>
YOUTUBE_API_VERSION = 'v3' <br>
YOUTUBE_API_KEY = 'XXXX' # replace with your actual YouTube API key <br>
CHANNEL_IDS = ['xxx', 'xxx', 'xxx'] # replace with actual YouTube channel IDs <br>

### Telegram
BOT_TOKEN = '000000000:AABBCCDDEEFFGGHHIIJJKKMMLLOOPPRRSS' # replace with your actual Telegram bot token <br>
TELEGRAM_CHANNEL_ID = -123456789 # replace with your actual Telegram channel ID <br>

### OpenAI
OPENAI_API_KEY = 'sk-xxx' # replace with your actual OpenAI API key <br>
PRIMARY_MODEL = 'gpt-3.5-turbo-16k' # replace with your preferred OpenAI model <br>
SECONDARY_MODEL = 'gpt-3.5-turbo' # replace with your preferred OpenAI model <br>

### Store file
STORE_FILE = 'video_store.txt'
