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


load_dotenv()

#Hidden Variables
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
AFFIRM_ID = int(os.getenv("AFFIRM_ID"))

# Global Variable
last_response_time = None

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

#bot jobs
@bot.event #bot started
async def on_ready():
    print(f"(*￣▽￣)~zzz... Huh? Net-chan is waking up... ☀️ *rubs eyes* Logged in as {bot.user}... Do I *have* to get up? (๑-﹏-๑)💤")

@bot.event  # bot responds to the webhook (maxed at once a minute)
async def on_message(message):
    global last_response_time

    # Skip the bot's own messages
    if message.author == bot.user:
        return

    # Allow the bot to process commands (such as the pet command) **before** applying custom logic
    await bot.process_commands(message)

    # Handle messages from the webhook user with rate-limiting logic
    webhook_user_id = 1342347016168280075

    if message.channel.id == CHANNEL_ID and message.author.id == webhook_user_id:
        current_time = asyncio.get_event_loop().time()

        if last_response_time and current_time - last_response_time < 60:
            return  # Don't reply if less than 60 seconds have passed
        else:
            await asyncio.sleep(3)
            reply = get_response("unraid", "") 
            if message.channel:
                await message.channel.send(reply)
            last_response_time = current_time



# bot commands
@bot.command()
async def pet(ctx):
    await ctx.send("Net-chan purrs and says thank you for the love! (｡♥‿♥｡)")

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