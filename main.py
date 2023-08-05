import os
import openai
import config
import logging
import telebot
import vertexai
from rich import print
from typing import List, Dict
from rich.logging import RichHandler
from dataclasses import dataclass, field
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from vertexai.language_models import TextGenerationModel

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY

@dataclass
class VideoInfo:
    id: str
    channel: str
    title: str
    url: str
    transcript: str = field(default_factory=str, init=False)
    summary: str = field(default_factory=str, init=False)

@dataclass
class Bot:
    youtube: object = field(default_factory=object, init=False)
    openai: object = field(default_factory=object, init=False)
    bot: object = field(default_factory=object, init=False)

    def __post_init__(self):
        self.youtube = build(config.YOUTUBE_API_SERVICE_NAME, config.YOUTUBE_API_VERSION, developerKey=config.YOUTUBE_API_KEY)
        self.openai = openai
        self.openai.api_key = config.OPENAI_API_KEY
        self.bot = telebot.TeleBot(config.BOT_TOKEN)

    def get_stored_videos(self) -> List[str]:
        """
        Retrieve stored video IDs from file
        """
        if os.path.exists(config.STORE_FILE):
            with open(config.STORE_FILE, 'r') as f:
                lines = f.read().splitlines()
            return lines
        else:
            return []

    def store_video(self, video_id: str) -> None:
        """
        Store video id to file
        """
        with open(config.STORE_FILE, 'a') as f:
            f.write('\n' + video_id)

    def get_latest_videos(self) -> List[VideoInfo]:
        """
        Get latest videos from specific channels
        """
        try:
            search_response = []
            for channel_id in config.CHANNEL_IDS_FILTER:
                search_response.append(self.youtube.search().list(
                    channelId=channel_id,
                    part='id,snippet',
                    maxResults=1,  # change this to retrieve more or less videos
                    order='date'  # ensures that the latest videos are retrieved
                ).execute())
            
            videos = []
            
            for response in search_response:
                for item in response.get('items'):
                    video_id = item['id']['videoId']
                    filtered_video = self.filter_old_videos(new_video=video_id)
                    if filtered_video is True:
                        video = VideoInfo(
                        id = item['id']['videoId'],
                        channel = item['snippet']['channelTitle'],
                        title = item['snippet']['title'],
                        url = f'https://www.youtube.com/watch?v={item["id"]["videoId"]}')
                        videos.append(video)
                        self.store_video(video_id=video_id)
            if not videos:
                log.info("No new Videos!")
            return videos
        except HttpError as e:
            log.info(f'An HTTP error {e.resp.status} occurred: {e.content}')
            return []

    def filter_old_videos(self, new_video):
        stored_videos = self.get_stored_videos()
        # Filter out videos that have been already processed
        if new_video not in stored_videos:
            return True
        return False
    
    def get_transcript(self, videos: List[VideoInfo]) -> None:
        for script in videos:
            transcript_list = YouTubeTranscriptApi.list_transcripts(script.id)
            result = [transcript.translate('en').fetch()[0]["text"]
                            for transcript in transcript_list]
            script.transcript = (''.join(result))
        return videos

    def generate_key_takeaways_openai(self, videos: List[VideoInfo]) -> None:
        for script in videos:
            completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "Extract key takeaways of the next chunk of the transcript. Each key takeaway should be a list item, of the following format:\n'- [takeaway]'\n. Do not use numbered lists and do not render brackets."},
                {"role": "user", "content": script.transcript}
            ])
            response1 = completion.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # script.summary = self._translate_vertex(transcript=response1)
            
            completion2 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Translate the following to Croatian."},
                {"role": "user", "content": response1}
            ])
            if len(completion2.get('choices', [{}])[0].get('message', {}).get('content', '')) > 500:
                script.summary = completion2.get('choices', [{}])[0].get('message', {}).get('content', '')
        return videos

    def _translate_vertex(self, transcript) -> None:
        vertexai.init(project="<google-cloud-vertex-id>", location="us-central1")
        parameters = {
            "temperature": 0.0,
            "max_output_tokens": 2048,
            "top_p": 0.8,
            "top_k": 40
        }
        model = TextGenerationModel.from_pretrained("text-bison@001")
        response = model.predict(
            f"""
            Translate the following text to croatian:
            {transcript}
            """,
            **parameters
        )
        return response.text

    def send_to_telegram(self, takeaways: Dict[VideoInfo, str]) -> None:
        """
        Send key takeaways to a Telegram channel
        """
        bot = telebot.TeleBot(token=config.BOT_TOKEN)
        if takeaways:
            for t in takeaways:
                bot.send_message(config.TELEGRAM_CHANNEL_ID, t.url)
                bot.send_message(config.TELEGRAM_CHANNEL_ID, t.summary)
            log.info("Telegram message sent!")

    def process_new_videos(self) -> None:
        """
        Main processing method
        """
        try:
            videos = self.get_latest_videos()
            scripts = self.get_transcript(videos=videos)
            takeaways = self.generate_key_takeaways_openai(videos=scripts)
            self.send_to_telegram(takeaways=takeaways)
        except Exception as e:
            log.info(f"An error occurred: {e}")

def main():
    bot = Bot()
    bot.process_new_videos()
    # for testing
    # videos = bot.get_latest_videos()
    # scripts = bot.get_transcript(videos=videos)
    # takeaways = bot.generate_key_takeaways(videos=scripts)
    # bot.send_to_telegram(takeaways=takeaways)
    
if __name__ == '__main__':
    main()
