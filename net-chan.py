# ==================================================================================
# IMPORTS AND SETUP
# ==================================================================================
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
from better_profanity import profanity
import re
import base64
# ==================================================================================
# CONSTANTS AND CONFIGURATION
# ==================================================================================
# File Paths
ART_DELAY_FILE = "./memory/art_delay.json"
WAKE_DELAY_FILE = "./memory/wake_delay.json"
KNOWN_USERS = "./memory/known_users.json"

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
AFFIRM_ID = int(os.getenv("AFFIRM_ID"))

# ==================================================================================
# GLOBAL VARIABLES
# ==================================================================================
last_response_time = None
last_response_time_lock = asyncio.Lock()
last_wake_message_time = None
wake_message_lock = asyncio.Lock()
praise_counter = 1
art_count = 0
webhook_log = []
MAX_LOG_SIZE = 100

# ==================================================================================
# DISCORD BOT SETUP
# ==================================================================================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==================================================================================
# HELPER FUNCTIONS
# ==================================================================================
# ----------------------------------------------------------------------------------
# Response Management
# ----------------------------------------------------------------------------------
def get_response(event_type, message):
    if os.path.exists('./responses.json'):
        with open('./responses.json', 'r') as f:
            json_data = json.load(f)
    else:
        json_data = {}

    if event_type in json_data:
        responses = json_data[event_type]
        response = random.choice(responses)
    else:
        response = "🌸 **Net-chan Update!** 🌸"
    if '{message}' in response:
            response = response.format(message=f"\n\n({message})")
    return response.replace("\\n", "\n")

# ----------------------------------------------------------------------------------
# Profanity Filter
# ----------------------------------------------------------------------------------
profanity.load_censor_words()

CHAR_SUBSTITUTIONS = str.maketrans("4301$@!", "aeolsai")

def normalize_text(text: str) -> str:
    text = text.lower().translate(CHAR_SUBSTITUTIONS)
    text = re.sub(r"[^a-z0-9\s]", "", text) 
    text = re.sub(r"\s+", " ", text).strip() 
    return text

def naughty_naughty(input_text: str) -> bool:
    cleaned_text = normalize_text(input_text)

    if profanity.contains_profanity(cleaned_text):
        return True

    spaced_out_check = re.search(r"\b([a-z])\s*([a-z])\s*([a-z])\s*([a-z])\s*([a-z])\b", cleaned_text)
    if spaced_out_check and profanity.contains_profanity("".join(spaced_out_check.groups())):
        return True

    return False

# ----------------------------------------------------------------------------------
# User Profile Management
# ----------------------------------------------------------------------------------
def load_profiles():
    if os.path.exists(KNOWN_USERS):
        if os.stat(KNOWN_USERS).st_size == 0:
            print(f"Warning: {KNOWN_USERS} is empty.")
            return {}
        
        try:
            with open(KNOWN_USERS, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Error: {KNOWN_USERS} contains invalid JSON.")
            return {}
    return {}


def save_profiles():
    with open(KNOWN_USERS, "w") as file:
        json.dump(user_profiles, file, indent=4)

class ProfileView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="✨ Create My Profile! ✨", style=discord.ButtonStyle.primary)
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ProfileModal())

class ProfileModal(discord.ui.Modal, title="✨ Sign Net-chan's Book 'o Besties! ✨"):
    name = discord.ui.TextInput(label="What's your name? (｡♥‿♥｡)", required=True)
    favorite_color = discord.ui.TextInput(label="What's your favorite color? (´∩｡• ᵕ •｡∩`)", required=True)
    favorite_animal = discord.ui.TextInput(label="What's your favorite animal? (｡♥‿♥｡)", required=True)
    favorite_food = discord.ui.TextInput(label="What's your favorite food? (๑˃̵ᴗ˂̵)", required=True)
    interests = discord.ui.TextInput(label="What are your interests? (´｡• ᵕ •｡`)", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        fields = [self.name.value, self.favorite_color.value, self.favorite_animal.value, 
                  self.favorite_food.value, self.interests.value]
        
        for field in fields:
            if naughty_naughty(field):
                await interaction.response.send_message(
                    "Oopsie~! It looks like you used some bad words.\n(｡•́︿•̀｡)\nPlease try again without those!",
                    ephemeral=True
                )
                return
        
        user_id = str(interaction.user.id)
        user_profiles[user_id] = {
            "name": self.name.value,
            "favorite_color": self.favorite_color.value,
            "favorite_animal": self.favorite_animal.value,
            "favorite_food": self.favorite_food.value,
            "interests": self.interests.value,
        }
        save_profiles()
        await interaction.response.send_message(
            f"Profile created! ✨\n**Name:** {self.name.value}\n"
            f"**Favorite Color:** {self.favorite_color.value}\n"
            f"**Favorite Animal:** {self.favorite_animal.value}\n"
            f"**Favorite Food:** {self.favorite_food.value}\n"
            f"**Interests:** {self.interests.value}",
            ephemeral=True
        )

user_profiles = load_profiles()

# ----------------------------------------------------------------------------------
# Delay Management
# ----------------------------------------------------------------------------------
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
    if not os.path.exists(ART_DELAY_FILE):
        with open(ART_DELAY_FILE, "w") as file:
            json.dump({}, file)
    save_delay_time(ART_DELAY_FILE)

def load_last_wake_time():
    if not os.path.exists(WAKE_DELAY_FILE):
        with open(WAKE_DELAY_FILE, "w") as file:
            json.dump({}, file)
    last_time = load_delay_time(WAKE_DELAY_FILE)
    if last_time is None:
        print("No previous wake time found, initializing to None.")
    return last_time

def save_last_wake_time():
    if not os.path.exists(WAKE_DELAY_FILE):
        with open(WAKE_DELAY_FILE, "w") as file:
            json.dump({}, file)
    save_delay_time(WAKE_DELAY_FILE)
    print(f"Saved last_wake_message_time to file.")

def is_new_day(last_timestamp):
    if not last_timestamp:
        return True
    
    last_date = last_timestamp.date()
    current_date = datetime.now().date()
    
    return current_date > last_date

# ----------------------------------------------------------------------------------
# Music Handling
# ----------------------------------------------------------------------------------
def get_song():
    if os.path.exists('./responses.json'):
        with open('./responses.json', 'r') as f:
            json_data = json.load(f)
            return(random.choice(json_data))
    else:
        return(None)

# ==================================================================================
# DISCORD BOT EVENTS
# ==================================================================================
@bot.event
async def on_ready():
    global last_wake_message_time
    global user_profiles
    user_profiles = load_profiles()
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
                embed = discord.Embed(description=wake_message, color=discord.Color.blue())
                file=discord.File('./images/net-chan-sleepy.png', filename="net-chan-sleepy.png")
                embed.set_image(url="attachment://net-chan-sleepy.png")
                await channel.send(embed=embed, file=file)
                last_wake_message_time = current_time
                save_last_wake_time()
                print(f"Sent wake message and updated last_wake_message_time to: {last_wake_message_time}")

@bot.event
async def on_message(message):
    global last_response_time
    global webhook_log

    if message.author == bot.user:
        return

    await bot.process_commands(message)

    webhook_user_id = int(os.getenv("WEBHOOK_BOT_ID"))

    if message.channel.id == CHANNEL_ID and message.author.id == webhook_user_id:
        current_time = asyncio.get_event_loop().time()

        if last_response_time and current_time - last_response_time < 60:
            return 

        last_response_time = current_time
        await asyncio.sleep(2)

        print(f"Message author: {message.author}")
        print(f"Message content: {message.content}")
        print(f"Message embeds: {message.embeds}")

        embed = None
        reply = None

        if message.embeds: 
            embed = message.embeds[0]
            embed_title = embed.title.lower() if embed.title else ""

            for field in embed.fields:
                print(f"Field Name: {field.name}, Value: {field.value}")

            log_message = f"{embed_title}: {embed.description if embed.description else 'No description'}"
            print(log_message)
            webhook_log.append(log_message)

            if "up" in embed_title:
                reply = get_response("kuma", "")
                color = discord.Color.green()
            elif "down" in embed_title:
                reply = get_response("fire", "")
                color = discord.Color.red()
            else:
                reply = get_response("unraid", "")
                color = discord.Color.purple()
        else:
            message_content = message.content.strip().lower()
            print(f"Message content after cleaning: {message_content}")

            if any(keyword in message_content for keyword in ['error', 'down', 'errors']):
                reply = get_response("fire", "")
                color = discord.Color.red()
            elif 'up' in message_content:
                reply = get_response("kuma", "")
                color = discord.Color.green()
            else:
                reply = get_response("unraid", "")
                color = discord.Color.purple()

            webhook_log.append(message_content)

        if reply:
            embed = discord.Embed(description=reply, color=color)
            await message.channel.send(embed=embed)

# ==================================================================================
# BACKGROUND TASKS
# ==================================================================================
async def send_positive_messages():
    await bot.wait_until_ready()
    
    while not bot.is_closed():
        now = datetime.now()
        daytime_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
        daytime_end = now.replace(hour=20, minute=0, second=0, microsecond=0)

        channel = bot.get_channel(AFFIRM_ID)
        
        if daytime_start <= now <= daytime_end:
            if channel:
                try:
                    positive_message = get_response("affirmations", "")
                    embed = discord.Embed(description=positive_message, color=discord.Color.purple())
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"Failed to send affirmation message: {e}")
            wait_time = random.randint(6 * 3600, 12 * 3600)
            await asyncio.sleep(wait_time)
        else:
            if now < daytime_start:
                wait_for_daytime = (daytime_start - now).seconds
            else:
                wait_for_daytime = (daytime_start + timedelta(days=1) - now).seconds

            await asyncio.sleep(wait_for_daytime)

async def reset_praise_counter():
    global praise_counter
    while True:
        await asyncio.sleep(60 * 60)
        praise_counter = 1
        print("Praise counter reset to 1.")

# ==================================================================================
# CUSTOM HELP COMMAND
# ==================================================================================
class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Net-chan Help", description="Here are the things I can do~! (*^ω^*):")
        
        command_list = (
    "✨ `!help` - Shows this help message. (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧\n"
    "✨ `!info` - Learn more about me! (◕‿◕✿)\n"
    "✨ `!register` - Create a sparkling profile with me! •ᴗ•\n"
    "✨ `!whoami` - Check my memory about you! ╰ (´꒳`) ╯ \n"
    "✨ `!deleteme` - Delete your profile! 💔 (╥﹏╥)\n"
    "✨ `!log` - Check the server event logs! ʕ•ᴥ•ʔ\n"
    "✨ `!art` - I'll make a cute picture! (◠﹏◠✿)\n"
    "✨ `!cheer` - I'll cheer you on! ヽ(•‿•)ノ\n"
    "✨ `!pat` - Hey, I'm working! (｡•̀︿•́｡)\n"
    "✨ `!music` - See what Net-chan's playing right now! (>▽<) 🎶"
)

        
        embed.add_field(name="Commands:", value=command_list, inline=False)
        
        await self.context.send(embed=embed)

bot.help_command = CustomHelpCommand()

# ==================================================================================
# BOT COMMANDS
# ==================================================================================
# ----------------------------------------------------------------------------------
# Profile Commands
# ----------------------------------------------------------------------------------
@bot.command()
async def register(ctx):
    user_id = str(ctx.author.id)
    
    if user_id not in user_profiles:
        await ctx.send(
            f"✨ Oh my goodness~! A new friend I haven't met yet! ✧(≧ω≦)✧\n\n"
            f"Hi-hi, {ctx.author.name} (｡♥‿♥｡) I'm Net-chan, your super sparkly server manager! "
            f"Would you like to create a profile so I can remember you forever? \n人´∀｀)\n "
            f"It'll make me sooo happy! (≧◡≦)\n\n"
            f"Just click the shiny button below and we can get started! ✨"
            f" I can't wait to be besties~! (๑˃̵ᴗ˂̵)"
            f" 💖💫",
            view=ProfileView()
        )
    else:
        await ctx.send(
            f"Heehee~! I already know you, silly {ctx.author.name}! (≧◡≦) ✨"
            f" Your profile is already all set in my sparkly database! (｡♥‿♥｡) 🎉"
        )


@bot.command()
async def whoami(ctx):
    user_id = str(ctx.author.id)
    profile = user_profiles.get(user_id)
    if profile:
        embed = discord.Embed(title=f"✨Yay~! {ctx.author.name}'s Profile!✨ (｡♥‿♥｡)", color=discord.Color.blue())
        embed.add_field(name="Name", value=profile["name"], inline=False)
        embed.add_field(name="Favorite Color", value=profile["favorite_color"], inline=False)
        embed.add_field(name="Favorite Animal", value=profile["favorite_animal"], inline=False)
        embed.add_field(name="Favorite Food", value=profile["favorite_food"], inline=False)
        embed.add_field(name="Interests", value=profile["interests"], inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Eh?! (・ε・) Net-chan doesn't know you yet! ┗(･ω･;)┛ Make a profile by using `!register` so we can be besties~! (人´∀｀)✨")


@bot.command()
async def deleteme(ctx):
    user_id = str(ctx.author.id)
    if user_id in user_profiles:
        del user_profiles[user_id]
        save_profiles()
        await ctx.send("Uuuuugh~! (╥﹏╥) Net-chan's deleting profiles... Soooo sad... Your profile is gone now! 💔💻💨")
    else:
        await ctx.send("Eh? (・_・;) You don't have a profile to delete, silly~! Maybe it's hiding somewhere? ( ´•̥̥̥ω•̥̥̥` )")


# ----------------------------------------------------------------------------------
# Log Commands
# ----------------------------------------------------------------------------------
@bot.command()
async def log(ctx):
    global webhook_log
    print(webhook_log) 
    if not webhook_log:
        log_text = "No recent webhooks received. (╯︵╰,)"
        border_color = discord.Color.red()
    else:
        recent_logs = [str(entry) for entry in webhook_log[-5:]]
        log_text = "\n".join(recent_logs)
        border_color = discord.Color.green()

    embed = discord.Embed(title="Webhook Log", description=log_text, color=border_color)
    await ctx.send(embed=embed)

# ----------------------------------------------------------------------------------
# Interaction Commands
# ----------------------------------------------------------------------------------
@bot.command()
async def pat(ctx):
    global praise_counter
    pat_image = './images/net-chan-embarassed.png'

    if praise_counter == 0:
        pat_reply = get_response("pat_annoyed", "")
        pat_image = './images/net-chan-angry.png'
        embed_color = discord.Color.red()
    else:
        pat_reply = get_response("pat", "")
        embed_color = discord.Color.green()
    
    embed = discord.Embed(description=pat_reply, color=embed_color)
    file = discord.File(pat_image, filename="net-chan.png")
    embed.set_image(url="attachment://net-chan.png")

    await ctx.send(embed=embed, file=file)
    
    praise_counter = 0

@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title="Let me tell you a bit about myself! (｡•̀ᴗ•́｡)", 
        description="Hehe~! (*≧ω≦)",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="✨ I'm Net-chan, your friendly server bot! ✨", 
        value=(
            "My main job is to send you updates about your homelab environment. I share and respond to server webhooks, "
            "and I notify you when certain scripts have run, but I'm learning to do more every day, whether it's answering "
            "questions, giving you updates, or just being super cute~! (*^ω^*)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="💖 My Love for Sparkles 💖", 
        value=(
            "I absolutely love sparkles, blinking lights, and bright colors! (｡♥‿♥｡) So if you see me getting excited, "
            "it's probably because something sparkly is happening~! (๑•́⌓•̀๑)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="Need Help?", 
        value=(
            "If you ever need anything, just type `!help`` and I'll be right here, ready to brighten your day! "
            "(｡•̀ᴗ•́｡)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="Cheer Up!", 
        value="And if you're feeling down, don't worry—I'll be here to cheer you up with my sparkly energy! (灬º‿º灬)♡", 
        inline=False
    )

    await ctx.send(embed=embed, file=discord.File('./images/net-chan.png'))

@bot.command()
async def cheer(ctx):
    cheer_message = get_response("affirmations", "")
    
    embed = discord.Embed(description=cheer_message, color=discord.Color.blue())
    await ctx.send(embed=embed)

# ----------------------------------------------------------------------------------
# Art Command
# ----------------------------------------------------------------------------------
@bot.command()
async def art(ctx):
    global art_count
    art_left = 5-art_count
    user_id = str(ctx.author.id)
    profile = user_profiles.get(user_id)
    last_art_time = load_last_art_time()

    if is_new_day(last_art_time):
        art_count = 0
        save_last_art_time()


    if art_count > 6:
        embed = discord.Embed(
            description="I'm too tired to make more art right now... I'm busy with other things. Maybe later? (｡•́︿•̀｡)",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    v_api = os.getenv('VENICE_API')
   
    if profile:
        embed = discord.Embed(title=f"✨Yay~! {ctx.author.name}'s Profile!✨ (｡♥‿♥｡)", color=discord.Color.blue())
        embed.add_field(name="Name", value=profile["name"], inline=False)

    cute_nouns = ["kitten", "puppy", "bunny", "baby", "cloud", "star", "bear", "butterfly", "kittens", "cupcake", "flower", "chick", "cookie", "birdie", "deer", "panda", "frog", "koala", "rainbow", "daisy", "lamb", "honeybee", "squirrel", "sunflower", "pony", "snowflake", "pup", "sparkle", "dream", "lollipop", "rose", "buttercup", "jellybean", "baby chick", "puddle", "treasure", "snail"]
    cute_adjectives = ["fluffy", "sparkly", "adorable", "sweet", "charming", "gentle", "playful", "soft", "lovely", "cute", "happy", "bright", "snuggly", "fuzzy", "cheerful", "whimsical", "delightful", "tender", "shiny", "rosy", "tasty", "warm", "peppy", "breezy", "magical", "sweetheart", "fluffy", "giddy", "colorful", "lovable", "bouncy", "calm", "pretty", "cozy", "fresh", "gentle", "glowy", "smiley", "sparkling", "twin", "friendly", "graceful", "carefree", "dazzling", "snug", "dreamy", "sunny", "puffy", "jolly", "mellow"]
    cute_objects = ["heart", "balloon", "cupcake", "cookie", "star", "cloud", "teddy bear", "rainbow", "flower", "blanket", "butterfly", "headband", "whisk", "paintbrush", "camera", "bookmark", "gloves", "pajamas", "purse", "necklace", "hat", "scarf", "bowtie", "sticker", "guitar", "mug", "pencil case", "ball", "glitter", "cup", "note", "book", "bottle", "jewelry", "pen", "notepad", "sweets", "keychain", "coin", "bracelet", "flowerpot", "diary", "mirror", "bottle","snow globe", "painting", "clock"]
    
    #Customize art with user profile if available
    if profile: 
        if random.random() < 0.7:
            adjective = random.choice(cute_adjectives)
        else:
            adjective = profile["favorite_color"]
    else:
        adjective = random.choice(cute_adjectives)
   
    if profile: 
        if random.random() < 0.7:
            noun = random.choice(cute_nouns)
        else:  
            noun = profile["favorite_animal"]
    else:
        noun = random.choice(cute_nouns)
    
    if profile: 
        if random.random() < 0.7:
            object_ = random.choice(cute_objects)
        else:  
            object_ = profile["favorite_food"]
    else:
        object_ = random.choice(cute_objects)
    
    
    prompt = f"a {adjective} {noun} with a {object_} in a very kawaii style"
    
    print(prompt)

    working_embed = discord.Embed(
        description="Hold on! I'm making something cute for you! 🎨✨ (this might take a moment...)",
        color=discord.Color.blue()
    )
    working_message = await ctx.send(embed=working_embed)

    try:
        url = "https://api.venice.ai/api/v1/image/generate"
        payload = {
            "model": "flux-dev",
            "prompt": prompt,
            "style_preset": "Anime",
            "height": 600,
            "width": 600,
            "steps": 20,
            "cfg_scale": 7.5,
            "seed": 123456789,
            "lora_strength": 50,
            "safe_mode": True,
            "return_binary": False,
            "hide_watermark": True,
            "format": "webp",
            "embed_exif_metadata": False,
        }
        headers = {
            "Authorization": f"Bearer {v_api}",
            "Content-Type": "application/json"
        }

        # Make the API request
        response = requests.request("POST", url, json=payload, headers=headers)
        
        if response.status_code != 200:
            error_embed = discord.Embed(
                description="Oopsie, there was an issue fetching the art... (｡•́︿•̀｡)",
                color=discord.Color.red()
            )
            await working_message.edit(embed=error_embed)
            return

        # Parse the JSON response
        response_data = response.json()
        
        # Extract the image data from the 'images' array
        if "images" in response_data and response_data["images"]:
            # The first image in the array contains the base64 data
            base64_data = response_data["images"][0]
            
            # Decode the base64 data
            image_data = base64.b64decode(base64_data)
            
            # Open the image from the decoded data
            image = Image.open(io.BytesIO(image_data))
            
            # Continue with saving and sending the image
            with io.BytesIO() as image_file:
                image.save(image_file, format="PNG")
                image_file.seek(0)
                
                art_embed = discord.Embed(
                    title=f"Here's your cute art, {ctx.author.name}! (｡♥‿♥｡)\nI can make {art_left} more pieces today!",
                    color=discord.Color.purple()
                )
                file = discord.File(image_file, filename="cute_art.png")
                art_embed.set_image(url="attachment://cute_art.png")
                
                await working_message.edit(embed=art_embed)
                await ctx.send(file=file)
                art_count +=1
        else:
            raise ValueError("No images found in the response")
            
    except Exception as e:
        error_embed = discord.Embed(
            description="I don't feel like doing art right now... 😔",
            color=discord.Color.red()
        )
        await working_message.edit(embed=error_embed)
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
# ----------------------------------------------------------------------------------
# Music Command
# ----------------------------------------------------------------------------------
@bot.command()
async def music(ctx):
    song = get_song()
    song_messages = [
        f"Nyaa~! (≧◡≦) Net-chan is listening to {song.get('title')} by {song.get('artist')}! 🎶✨ It's so fun, it makes me wanna dance! (✿◕‿◕)💾🎵 Will you listen too, pwease? (๑•́‧̫•̀๑) 👉 {song.get('link')}",
        f"U-uhm... (⁄ ⁄•⁄ω⁄•⁄ ⁄) Net-chan found a really nice song... it's {song.get('title')} by {song.get('artist')}! 🎶💜 It makes me feel all warm inside~ (*≧ω≦)✨ M-maybe you can listen too...? I-if you want to... 👉 {song.get('link')} 💕",
        f"Waah~! (ﾉ´ヮ`)ﾉ*:･ﾟ✧ {song.get('title')} by {song.get('artist')} is soooo good!! 🎶💾 My circuits are all tingly~! (๑>ᴗ<๑) Heehee~ will you listen with me, pwease? (✿˶˘ ᴗ ˘˶)💜👉 {song.get('link')}",
        f"Heehee~! (✿◕‿◕) Net-chan found a super cool song—it's {song.get('title')} by {song.get('artist')}! 🎶💾 I feel so happy when I listen to it~!! (๑˃̵ᴗ˂̵)✨ Wanna listen with me, bestie? (｡♥‿♥｡) 👉 {song.get('link')}",
        f"Uwu~! Net-chan's circuits are vibing to {song.get('title')} by {song.get('artist')}! ⚡🎶 You should totally listen too, nya~! 💾💜 Clicky-click here! 👉 {song.get('link')}"
    ]
    
    if not song:
        song_message = "Uuuughhh~! (╥﹏╥) I haven’t had any time to dig up fresh bangers…! My playlist is just dusty old tracks on repeat~! ✨💿💔 Sooo lame...!! (ಥ﹏ಥ) Pls don’t ask me for recs rn, I got nothin’! 💀💿💨"
        embed = discord.Embed(description=song_message, color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        song_message = random.choice(song_messages)
        embed = discord.Embed(description=song_message, color=discord.Color.blue())
        file = discord.File(song.get('image'), filename="album_cover.jpg")
        embed.set_image(url="attachment://album_cover.jpg")
        await ctx.send(embed=embed, file=file)

# ==================================================================================
# FLASK WEBHOOK HANDLING
# ==================================================================================
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    global webhook_log
    data = request.json
    message = data.get("message", "No details provided.")
    event_type = data.get("event", "generic")
    reply = get_response(event_type, message)

    print(f"Received event_type: {event_type}, message: {message}")
    
    log_entry = f"{event_type}: {message}"
    webhook_log.append(log_entry)
    
    if len(webhook_log) > 100:
        webhook_log = webhook_log[-100:]

    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        embed = discord.Embed(description=reply, color=discord.Color.blue())
        embed.add_field(name="Event Type", value=event_type, inline=False)
        embed.add_field(name="Message", value=message, inline=False)

        asyncio.run_coroutine_threadsafe(channel.send(embed=embed), bot.loop)

    return {"status": "ok"}

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False)

# ==================================================================================
# MAIN EXECUTION
# ==================================================================================
if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(TOKEN)