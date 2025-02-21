import os
import discord
from discord.ext import commands
from flask import Flask, request
import asyncio
from threading import Thread
from dotenv import load_dotenv
from responses import get_response
from datetime import datetime, timedelta
import random
import requests
import io
from PIL import Image


load_dotenv()

#Hidden Variables
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
AFFIRM_ID = int(os.getenv("AFFIRM_ID"))


# Global Variable
last_response_time = None
last_response_time_lock = asyncio.Lock()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Net-chan is ready! Logged in as {bot.user}")
    
    channel = bot.get_channel(CHANNEL_ID)
    
    if channel:
        # Send a message along with an image (URL)
        wake_message = get_response("wake", "")
        await channel.send(
            wake_message,
            file=discord.File('./images/net-chan.png')  # Use the correct path to your image
        )
    else:
        print("Channel not found!")



@bot.event  # bot responds to the unfiltered webhook (maxed at once a minute)
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
            await asyncio.sleep(3)
            reply = get_response("unraid", "") 
            if message.channel:
                await message.channel.send(reply)
            last_response_time = current_time

@bot.event
async def on_disconnect():
    print("Bot disconnected, cleaning up...")


# bot commands
@bot.command()
async def commands(ctx):
    help_message = """
    Hehe~! (*≧ω≦) Here are the things I can do for you~! (*^ω^*)

    ✨ `!commands` - Aww, you wanna know what I can do? Here's all my little tricks! (｡•̀ᴗ•́｡)✨
    ✨ `!pat` - W-Wait, don't do that! I'm working! (｡•̀︿•́｡) But... maybe just a little pat... for being so sweet? (//∇//) 
    ✨ `!cheer` - Need a little pick-me-up? I'll send you a cute and affirming message! (｡♥‿♥｡)
    ✨ `!art` - I can draw something just for you~! Maybe something sparkly? (｡•́︿•̀｡)✨
    ✨ `!info` - Wanna know more about me? (´｡• ᵕ •｡`) I’d love to share~! (*´ω`*)

    I’m always here for you, so let me know if you need anything else! (´∩｡• ᵕ •｡∩`)✨
    """
    await ctx.send(help_message)


@bot.command()
async def pat(ctx):
    await ctx.send("W-What do you think you're doing...! (｡•̀︿•́｡) J-just a headpat, huh?... F-fine, I guess I appreciate it... (//∇//) *looks away*")

@bot.command()
async def info(ctx):
    await ctx.send("""
    Hehe~! (*≧ω≦) Let me tell you a bit about myself! (｡•̀ᴗ•́｡)✨

    ✨ I'm Net-chan, your friendly server bot! ✨
    My main job is to send you updates about your homelab environment. I share and respond to server webhooks, and I notify you when certain scripts have run, but I'm learning to do more every day, whether it's answering questions, giving you updates, or just being super cute~! (*^ω^*)

    ✨ I absolutely love sparkles, blinking lights, and bright colors! (｡♥‿♥｡) So if you see me getting excited, it’s probably because something sparkly is happening~! (๑•́⌓•̀๑)

    ✨ If you ever need anything, just type `!commands` and I'll be right here, ready to brighten your day! (｡•̀ᴗ•́｡)✨

    ✨ And if you’re feeling down, don’t worry—I'll be here to cheer you up with my sparkly energy! (灬º‿º灬)♡
    """)

@bot.command()
async def cheer(ctx):
    cheer_message = get_response("affirmations", "")
    await ctx.send(cheer_message)

@bot.command()
async def art(ctx):
    hf_api = os.getenv('HUGGING_FACE_API')
    try:
        # API request to Hugging Face
        API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
        headers = {"Authorization": f"Bearer {hf_api}"}  # Using the API token from env var

        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload)
            return response

        # Request the image (description is customizable)
        response = query({
            "inputs": "something super cute that will make me say 'awwww, kawaii!'",
        })

        # Ensure the response was successful
        if response.status_code != 200:
            await ctx.send("Oops, there was an issue fetching the art from Hugging Face.")
            return

        # Check if the content is an image (content type header)
        if 'image' not in response.headers['Content-Type']:
            print("Received non-image data:")
            print(response.content)  # Log raw content for inspection
            await ctx.send("Oops, something went wrong with the art generation. Please try again later.")
            return

        # Open the image using PIL
        image = Image.open(io.BytesIO(response.content))

        # Save the image to an in-memory file to send in Discord
        with io.BytesIO() as image_file:
            image.save(image_file, format="PNG")
            image_file.seek(0)  # Go to the beginning of the file

            # Send the image to Discord
            await ctx.send("Here's your cute art! (｡♥‿♥｡)", file=discord.File(image_file, filename="cute_art.png"))

    except Exception as e:
        await ctx.send("I don't feel like doing art right now... 😔")
        print(f"Error occurred: {e}")


#monitoring
async def send_positive_messages(): #daily affirmations that are cute
    await bot.wait_until_ready()
    channel = bot.get_channel(AFFIRM_ID)
    
    while not bot.is_closed():

        now = datetime.now()
        
        daytime_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
        daytime_end = now.replace(hour=20, minute=0, second=0, microsecond=0)
        
        if daytime_start <= now <= daytime_end:

            wait_time = random.randint(0, (daytime_end - now).seconds) 
            await asyncio.sleep(wait_time)
            
            if channel:
                positive_message = get_response("affirmations", "")
                await channel.send(positive_message)
            await asyncio.sleep(random.randint(6 * 3600, 12 * 3600))  

        else:
            wait_for_daytime = (daytime_start - now).seconds if now < daytime_start else (daytime_start + timedelta(days=1) - now).seconds
            await asyncio.sleep(wait_for_daytime) 

#Flask
app = Flask(__name__)

#Flask routes
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


#Wake up, Net-chan!
if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(TOKEN)