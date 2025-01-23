import discord
from discord.ext import tasks
from discord import app_commands
from googleapiclient.discovery import build
import requests
import tempfile
import os
import asyncio
import config
from logging import getLogger

logger = getLogger(__name__)

# 必要なトークンやAPIキーを設定
DISCORD_TOKEN = config.DISCORD_TOKEN
YOUTUBE_API_KEY = config.YOUTUBE_API_KEY

# Discord Botの設定
intents = discord.Intents.default()
intents.voice_states = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# YouTube APIの初期化
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# VOICELOID関連関数
def post_audio_query(text: str, speaker: int):
    URL = "http://127.0.0.1:50021/audio_query"
    Parameters = {
        "text": text,
        "speaker": speaker
    }
    response = requests.post(URL, params=Parameters)
    return response.json()

def post_synthesis(json: dict, speaker: int):
    URL = "http://127.0.0.1:50021/synthesis"
    Parameters = {
        "speaker": speaker
    }
    response = requests.post(URL, json=json, params=Parameters)
    return response.content

def save_tempfile(text: str, speaker: int):
    json = post_audio_query(text, speaker)
    data = post_synthesis(json, speaker)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wf:
        wf.write(data)
        wf.close()
        return wf.name

# ライブチャットIDを取得
def get_live_chat_id(video_id):
    response = youtube.videos().list(
        part='liveStreamingDetails',
        id=video_id
    ).execute()
    items = response.get('items', [])
    if not items:
        return None
    live_details = items[0].get('liveStreamingDetails', {})
    return live_details.get('activeLiveChatId')

# ライブチャットメッセージを取得
def get_live_chat_messages(live_chat_id):
    response = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part='snippet,authorDetails'
    ).execute()
    return response.get('items', [])

# Discordの音声クライアント
voice_client = None

# 再生済みメッセージを記録
played_messages = set()

# コメント再生タスク
@tasks.loop(seconds=30)
async def fetch_and_play_comments(interaction, live_chat_id):
    global voice_client, played_messages
    if not live_chat_id:
        await interaction.channel.send("ライブチャットIDが無効です。")
        return

    try:
        print('コメント取得開始')
        messages = get_live_chat_messages(live_chat_id)
        print('コメント取得終了')

        # 取得したコメントの中で未読のものを処理
        for message in messages:
            message_id = message['id']  # メッセージの一意なID
            if message_id in played_messages:
                continue  # 既に再生済みのメッセージはスキップ

            # 未読コメントを再生し、記録
            played_messages.add(message_id)
            author = message['authorDetails']['displayName']
            text = message['snippet']['displayMessage']
            print(f"{author}: {text}")
            if voice_client and voice_client.is_connected():
                path = save_tempfile(f"{author} さん: {text}", 2)
                voice_client.play(discord.FFmpegPCMAudio(path), after=lambda e: os.remove(path))
                while voice_client.is_playing():
                    await asyncio.sleep(1)
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# スラッシュコマンド: ボイスチャンネルに接続
@tree.command(name="join", description="ボイスチャンネルに接続してYouTubeライブチャットを読み上げます。")
async def join(interaction: discord.Interaction, video_id: str):
    global voice_client, played_messages
    if not interaction.user.voice:
        await interaction.response.send_message("ボイスチャンネルに接続していません。", ephemeral=True)
        return

    live_chat_id = get_live_chat_id(video_id)
    if not live_chat_id:
        await interaction.response.send_message("ライブチャットIDが見つかりませんでした。", ephemeral=True)
        return

    played_messages.clear()  # 新しい動画の開始時に再生済みメッセージをクリア
    voice_channel = interaction.user.voice.channel
    voice_client = await voice_channel.connect()

    await interaction.response.send_message("ボイスチャンネルに接続しました。")
    path = save_tempfile("接続しました", 2)
    voice_client.play(discord.FFmpegPCMAudio(path), after=lambda e: os.remove(path))

    # コメント再生タスクを開始
    fetch_and_play_comments.start(interaction, live_chat_id)

# スラッシュコマンド: ボイスチャンネルから切断
@tree.command(name="leave", description="ボイスチャンネルから切断します。")
async def leave(interaction: discord.Interaction):
    global voice_client
    if voice_client:
        fetch_and_play_comments.stop()  # タスク停止
        await voice_client.disconnect()
        voice_client = None
        await interaction.response.send_message("ボイスチャンネルから切断しました。")
    else:
        await interaction.response.send_message("ボイスチャンネルに接続していません。", ephemeral=True)

# Bot起動時にスラッシュコマンドを同期
@bot.event
async def on_ready():
    await tree.sync()
    print(f"ログインしました: {bot.user}")

bot.run(DISCORD_TOKEN)
