# Imports
import os
import discord
from discord.ext import commands
from flask import Flask, request
import asyncio
from threading import Thread
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
import requests
import io
from PIL import Image
import json

# Constants
ART_DELAY_FILE = "./delays/art_delay.json"
WAKE_DELAY_FILE = "./delays/wake_delay.json"

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
AFFIRM_ID = int(os.getenv("AFFIRM_ID"))

# Global Variables
last_response_time = None
last_response_time_lock = asyncio.Lock()
last_wake_message_time = None
wake_message_lock = asyncio.Lock()

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Response Handling
def load_responses(file_name):
    if file_name:
        with open(file_name, 'r', encoding="utf-8") as file:
            responses = file.readlines()
        return [response.strip() for response in responses]
    else:
        return ["🌸 **Net-chan Update!** 🌸"]

def get_response(event_type, message):
    response_files = {
        "updates": './responses/update_responses.txt',
        "backup": './responses/backup_responses.txt',
        "sync": './responses/sync_responses.txt',
        "unraid": './responses/unraid_responses.txt',
        "failed": './responses/failure_responses.txt',
        "affirmations": './responses/affirmations.txt',
        "wake": './responses/wake_up.txt',
        "pat": './responses/pats.txt',
        "fire": './responses/fire.txt',
        "kuma": './responses/kuma.txt',
    }
    responses = load_responses(response_files.get(event_type, ''))
    response = random.choice(responses)
    if '{message}' in response:
        response = response.format(message=f"\n\n({message})")
    return response.replace("\\n", "\n")

# Art Prompt Generation
cute_nouns = ["kitten", "puppy", "bunny", "baby", "cloud", "star", "teddy bear", "angel", "butterfly", "kittens", "cupcake", "flower", "chick", "cookie", "birdie", "deer", "panda", "frog", "koala", "breeze", "rainbow", "daisy", "lamb", "honeybee", "squirrel", "sunflower", "pony", "smile", "snowflake", "heart", "whiskers", "pup", "glow", "sparkle", "snuggle", "giggle", "dream", "lollipop", "rose", "buttercup", "jellybean", "charm", "cuddle", "joy", "sunshine", "baby chick", "puddle", "giggle", "treasure", "snail"]
cute_adjectives = ["fluffy", "sparkly", "adorable", "sweet", "charming", "gentle", "playful", "soft", "lovely", "cute", "happy", "bright", "snuggly", "fuzzy", "cheerful", "whimsical", "delightful", "tender", "shiny", "rosy", "tasty", "warm", "peppy", "breezy", "magical", "sweetheart", "fluffy", "giddy", "colorful", "lovable", "bouncy", "calm", "pretty", "cozy", "fresh", "gentle", "glowy", "smiley", "sparkling", "twin", "friendly", "graceful", "carefree", "dazzling", "snug", "dreamy", "sunny", "puffy", "jolly", "mellow"]
cute_objects = ["heart", "balloon", "cupcake", "cookie", "star", "cloud", "socks", "teddy bear", "rainbow", "flower", "tissue box", "pillow", "blanket", "butterfly", "headband", "whisk", "paintbrush", "camera", "frame", "bookmark", "gloves", "pajamas", "purse", "necklace", "hat", "scarf", "bowtie", "sticker", "guitar", "lamp", "mug", "pencil case", "planner", "ball", "glitter", "cup", "note", "book", "bottle", "jewelry", "pen", "notepad", "sweets", "keychain", "coin", "bracelet", "flowerpot", "carpet", "diary", "mirror", "tumbler", "bottle", "lollipop", "snow globe", "painting", "clock"]

def generate_art_prompt():
    adjective = random.choice(cute_adjectives)
    noun = random.choice(cute_nouns)
    object_ = random.choice(cute_objects)
    return f"a {adjective} {noun} with a {object_}"

# Delay Handling
def load_delay_time(file_path):
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                last_time_str = data.get('last_time')
                if last_time_str:
                    return datetime.fromisoformat(last_time_str)
                else:
                    print(f"Key 'last_time' not found in {file_path}")
                    return None
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_path}: {e}")
            return None
    else:
        print(f"File {file_path} does not exist or is empty.")
        return None

def save_delay_time(file_path):
    last_time = datetime.now()
    with open(file_path, 'w') as file:
        json.dump({"last_time": last_time.isoformat()}, file)

def load_last_art_time():
    return load_delay_time(ART_DELAY_FILE)

def save_last_art_time():
    save_delay_time(ART_DELAY_FILE)

def load_last_wake_time():
    last_time = load_delay_time(WAKE_DELAY_FILE)
    if last_time is None:
        print("No previous wake time found, initializing to None.")
    return last_time

def save_last_wake_time():
    save_delay_time(WAKE_DELAY_FILE)
    print(f"Saved last_wake_message_time to file.")

# Discord Bot Events
@bot.event
async def on_ready():
    global last_wake_message_time
    print(f"Net-chan is ready! Logged in as {bot.user}")

    last_wake_message_time = load_last_wake_time()
    print(f"Loaded last_wake_message_time: {last_wake_message_time}")

    bot.loop.create_task(send_positive_messages())

    current_time = datetime.now()
    print(f"Current time: {current_time}")

    async with wake_message_lock:
        if last_wake_message_time is None or (current_time - last_wake_message_time) > timedelta(hours=1):
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                wake_message = get_response("wake", "")
                await channel.send(wake_message, file=discord.File('./images/net-chan-sleepy.png'))
                last_wake_message_time = current_time
                save_last_wake_time()
                print(f"Sent wake message and updated last_wake_message_time to: {last_wake_message_time}")

import re

@bot.event
async def on_message(message):
    global last_response_time

    if message.author == bot.user:
        return

    await bot.process_commands(message)

    webhook_user_id = int(os.getenv("WEBHOOK_BOT_ID"))

    if message.channel.id == CHANNEL_ID and message.author.id == webhook_user_id:
        current_time = asyncio.get_event_loop().time()

        if last_response_time and current_time - last_response_time < 60:
            return
        else:
            await asyncio.sleep(2)

            print(f"Message author: {message.author}")
            print(f"Message content: {message.content}")
            print(f"Message embeds: {message.embeds}")

            if message.embeds:
                embed = message.embeds[0]
                embed_title = embed.title.lower() if embed.title else ""

                print(f"Embed title: {embed_title}")

                if "up" in embed_title:
                    reply = get_response("kuma", "")
                elif "down" in embed_title:
                    reply = get_response("fire", "")
                else:
                    reply = get_response("unraid", "")

            else:
                message_content = message.content.strip().lower()
                print(f"Message content after cleaning: {message_content}")

                if any(keyword in message_content for keyword in ['error', 'down', 'errors']):
                    reply = get_response("fire", "")
                elif 'up' in message_content:
                    reply = get_response("kuma", "")
                else:
                    reply = get_response("unraid", "")

            if message.channel:
                await message.channel.send(reply)

            last_response_time = current_time


@bot.event
async def on_disconnect():
    print("Bot disconnected, cleaning up...")

# Discord Bot Commands
@bot.command()
async def commands(ctx):
    help_message = """
    Here are the things I can do for you~! (*^ω^*)
    ✨ `!commands` - This message!(*≧ω≦)
    ✨ `!pat` - Hey, I'm working! (｡•̀︿•́｡)
    ✨ `!cheer` - I'll cheer you on! (｡♥‿♥｡)
    ✨ `!art` - I'll make a cute picture! (*´ω`*)
    ✨ `!info` - Learn more about me! (◕‿◕✿) 

    I’m always here for you, so let me know if you need anything else!
    (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧
    """
    await ctx.send(help_message)
    
@bot.command()
async def pat(ctx):
    pat_reply = get_response("pat", "")
    await ctx.send(pat_reply, file=discord.File('./images/net-chan-embarassed.png'))

@bot.command()
async def info(ctx):
    command_message = """
    Hehe~! (*≧ω≦) 
    Let me tell you a bit about myself! (｡•̀ᴗ•́｡)

    ✨ I'm Net-chan, your friendly server bot! ✨
    
    My main job is to send you updates about your homelab environment. I share and respond to server webhooks, and I notify you when certain scripts have run, but I'm learning to do more every day, whether it's answering questions, giving you updates, or just being super cute~! (*^ω^*)
    
    I absolutely love sparkles, blinking lights, and bright colors! (｡♥‿♥｡) So if you see me getting excited, it’s probably because something sparkly is happening~! (๑•́⌓•̀๑)
    
    If you ever need anything, just type `!commands` and I'll be right here, ready to brighten your day! (｡•̀ᴗ•́｡)
    
    And if you’re feeling down, don’t worry—I'll be here to cheer you up with my sparkly energy! (灬º‿º灬)♡
    """
    await ctx.send(command_message, file=discord.File('./images/net-chan.png'))

@bot.command()
async def cheer(ctx):
    cheer_message = get_response("affirmations", "")
    await ctx.send(cheer_message)

@bot.command()
async def art(ctx):
    last_art_time = load_last_art_time()
    if last_art_time and datetime.now() - last_art_time < timedelta(hours=12):
        await ctx.send("I'm too tired to make more art right now... I'm busy with other things. Maybe later? (｡•́︿•̀｡)")
        return

    hf_api = os.getenv('HUGGING_FACE_API')
    prompt = generate_art_prompt()
    print(prompt)

    try:
        API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
        headers = {"Authorization": f"Bearer {hf_api}"}
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

        if response.status_code != 200:
            await ctx.send("Oopsie, there was an issue fetching the art... (｡•́︿•̀｡)")
            return

        image = Image.open(io.BytesIO(response.content))
        with io.BytesIO() as image_file:
            image.save(image_file, format="PNG")
            image_file.seek(0)
            await ctx.send("Here's your cute art! (｡♥‿♥｡)", file=discord.File(image_file, filename="cute_art.png"))

        save_last_art_time()
    except Exception as e:
        await ctx.send("I don't feel like doing art right now... 😔")
        print(f"Error occurred: {e}")

# Monitoring and Background Tasks
async def send_positive_messages():
    await bot.wait_until_ready()
    
    while not bot.is_closed():
        now = datetime.now()
        daytime_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
        daytime_end = now.replace(hour=20, minute=0, second=0, microsecond=0)

        # Fetch the channel inside the loop to ensure it's always up-to-date
        channel = bot.get_channel(AFFIRM_ID)
        
        if daytime_start <= now <= daytime_end:
            # Send a positive message
            if channel:
                try:
                    positive_message = get_response("affirmations", "")
                    await channel.send(positive_message)
                except Exception as e:
                    print(f"Failed to send affirmation message: {e}")

            # Wait for a random interval between 6 and 12 hours
            wait_time = random.randint(6 * 3600, 12 * 3600)
            await asyncio.sleep(wait_time)
        else:
            # Calculate time until the next daytime window
            if now < daytime_start:
                wait_for_daytime = (daytime_start - now).seconds
            else:
                wait_for_daytime = (daytime_start + timedelta(days=1) - now).seconds

            # Wait until the next daytime window
            await asyncio.sleep(wait_for_daytime)

# Flask Webhook Handling
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("message", "No details provided.")
    event_type = data.get("event", "generic")
    reply = get_response(event_type, message)
    print(f"Received event_type: {event_type}, message: {message}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        asyncio.run_coroutine_threadsafe(channel.send(reply), bot.loop)
    return {"status": "ok"}

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False)

# Main Execution
if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(TOKEN)