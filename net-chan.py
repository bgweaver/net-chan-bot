import os
import discord
from discord.ext import commands
from flask import Flask, request
import asyncio
from threading import Thread
from dotenv import load_dotenv
from responses import get_response

load_dotenv()

#Hidden Variables
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
UNRAID_ID = int(os.getenv("UNRAID_ID"))

# Global Variable
last_response_time = None

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

#bot events
@bot.event #bot started
async def on_ready():
    print(f"(*￣▽￣)~zzz... Huh? Net-chan is waking up... ☀️ *rubs eyes* Logged in as {bot.user}... Do I *have* to get up? (๑-﹏-๑)💤")

@bot.event  # bot responds to Unraid webhook (maxed at once a minute)
async def on_message(message):
    global last_response_time
    if message.author == bot.user:
        return
    
    if message.channel.id == UNRAID_ID:
        current_time = asyncio.get_event_loop().time()
        if last_response_time and current_time - last_response_time < 60:
            return
        else:
            await asyncio.sleep(3)
            reply = get_response("unraid", "") 
            if message.channel:
                await message.channel.send(reply)
            last_response_time = current_time
    
    await bot.process_commands(message)


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
    app.run(host="0.0.0.0", port=5000)

#Wake up, Net-chan!
if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(TOKEN)