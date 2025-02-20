import discord
from discord.ext import commands
from flask import Flask, request
import asyncio
import random
from threading import Thread
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
UNRAID_ID = int(os.getenv("UNRAID_ID"))

# Pool of responses for random replies
unraid_responses = [
    "Oops, I guess that was a bit too dry, huh? 😔 Sorry, that’s all the techy details for now... but I’ll be back with something more fun soon! (｡•́︿•̀｡)",
    "I tried to make it cute, but it’s just... not! 😩 sigh I promise, next time I’ll have something more exciting for you!",
    "Sooo... that was a bit too techy and dull, huh? 😓 Don’t worry though, I’ll be back with more kawaii updates soon! 💖",
    "Ugh, that was so boring! 😢 But it’s done. I’ll try to make it up to you with something cuter next time!",
    "Well, there you have it... just some tech stuff. yawn 😔 Hope you didn’t fall asleep! I’ll try harder next time, promise!",
    "Groan There it is... the dreaded unRAID status... 😩 I’ll be back with something way more exciting, I promise!",
    "Ugh, why does this tech stuff have to be so dull? 😔 Please forgive me! I’ll be more fun next time, I swear!",
    "Okay... that was pretty boring, huh? 😓 But the unRAID status is important, so I had to give it to you! Next time, I’ll make it more fun!",
    "Sigh Well, that was about as thrilling as watching a server update… 😢 But hey, the job’s done! I’ll be back with something much cuter soon, I hope!"
]

# Discord bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# A variable to track if the bot is waiting
last_response_time = None

@bot.event
async def on_ready():
    print(f"Net-chan is online! Logged in as {bot.user}")

@bot.event
async def on_message(message):
    global last_response_time

    # Prevent bot from responding to its own messages
    if message.author == bot.user:
        return

    # Check if the message is in the specified channel
    if message.channel.id == UNRAID_ID:
        current_time = asyncio.get_event_loop().time()

        # If the last response was within 60 seconds, ignore the new message
        if last_response_time and current_time - last_response_time < 60:
            return

        # Choose a random response from the pool
        response = random.choice(unraid_responses)

        # Send the random response
        await message.channel.send(response)

        # Update the last response time
        last_response_time = current_time

    # Process commands as well
    await bot.process_commands(message)

# Webhook server setup
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("message", "No details provided.")
    event_type = data.get("event", "generic")

    responses = {
    "docker_update": f"🐳 **Docker Updated!** 🐳\nNet-chan just updated your Docker containers! Time to keep things running smoothly!\n(◕‿◕)\n{message}",
    "docker_update_failed": f"⚠️ **Docker Update Failed!** ⚠️\nOopsie! Something went wrong while updating the Docker containers.\n(｡•́︿•̀｡) I'll try again! Stay tuned... \n{message}",
    "docker_backup": f"🛡️ **Docker Backed Up!** 🛡️\nNet-chan just finished backing up your Docker containers! No data losses allowed on my watch!\n(ﾉ◕ヮ◕)ﾉ:･ﾟ✧\n{message}",
    "docker_backup_failed": f"❌ **Docker Backup Failed!** ❌\nOh no! Net-chan tried her best, but something went wrong while backing up your Docker containers... \n(｡•́︿•̀｡) I'll try again, don't worry!\n{message}",
    "backblaze_backup": f"✨ **Backblaze Backup Complete!** ✨\nNet-chan successfully backed up your files to Backblaze! Your data is safe and sound!\n(｡•̀ᴗ-)✧\n{message}",
    "backblaze_backup_failed": f"🔥 **Backblaze Backup Failed!** 🔥\nUh-oh! Net-chan encountered an issue while backing up to Backblaze...\n(｡•́︿•̀｡) I'll fix it and try again!\n{message}",
    "generic": f"🌸 **Net-chan Update!** 🌸\n{message}",
    "unraid_sync_complete": f"💾 **Codebase Secured!** 💾\nNet-chan promises not to peek… okay, maybe just a little!\n(๑˃̵ᴗ˂̵)و\n{message}",
    "unraid_sync_failed": f"⚡ **Code Backup Failed** ⚡\nOopsie! Net-chan tried her best, but something went wrong with the codebase backup...\n(｡•́︿•̀｡) I\’ll try again, don’t worry!\n{message}",
}


    reply = responses.get(event_type, responses["generic"])

    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        asyncio.run_coroutine_threadsafe(channel.send(reply), bot.loop)

    return {"status": "ok"}

# Run bot and webhook together
def run_flask():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    # Start Flask webhook server in a separate thread
    Thread(target=run_flask).start()
    # Run the bot
    bot.run(TOKEN)
