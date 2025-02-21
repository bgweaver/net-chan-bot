import random
import os
from datetime import datetime
import json

ART_DELAY_FILE = "./delays/art_delay.json"
WAKE_DELAY_FILE = "./delays/wake_delay.json"

def load_responses(file_name):
    with open(file_name, 'r') as file:
        responses = file.readlines()
    return [response.strip() for response in responses]

def get_response(event_type, message):
    if event_type == "updates":
        responses = load_responses('./responses/update_responses.txt')
    elif event_type == "backup":
        responses = load_responses('./responses/backup_responses.txt')
    elif event_type == "sync":
        responses = load_responses('./responses/sync_responses.txt')
    elif event_type == "unraid":
        responses = load_responses('./responses/unraid_responses.txt')
    elif event_type == "failed":
        responses = load_responses('./responses/failure_responses.txt')
    elif event_type == "affirmations":
        responses = load_responses('./responses/affirmations.txt')
    elif event_type == "wake":
        responses = load_responses('./responses/wake_up.txt')   
    elif event_type == "pat":
        responses = load_responses('./responses/pats.txt')   
    
    else:
        responses = ["🌸 **Net-chan Update!** 🌸" + message]

    response = random.choice(responses)
    

    if '{message}' in response:
        response = response.format(message=f"\n\n({message})")
    
    return response.replace("\\n", "\n")


cute_nouns = [
    "kitten", "puppy", "bunny", "baby", "cloud", "star", "teddy bear", "angel", "butterfly", "kittens",
    "cupcake", "flower", "chick", "cookie", "birdie", "deer", "panda", "frog", "koala", "breeze",
    "rainbow", "daisy", "lamb", "honeybee", "squirrel", "sunflower", "pony", "smile", "snowflake", "heart",
    "whiskers", "pup", "glow", "sparkle", "snuggle", "giggle", "dream", "lollipop", "rose", "buttercup",
    "jellybean", "charm", "cuddle", "joy", "sunshine", "baby chick", "puddle", "giggle", "treasure", "snail"
]


cute_adjectives = [
    "fluffy", "sparkly", "adorable", "sweet", "charming", "gentle", "playful", "soft", "lovely", "cute",
    "happy", "bright", "snuggly", "fuzzy", "cheerful", "whimsical", "delightful", "tender", "shiny", "rosy",
    "tasty", "warm", "peppy", "breezy", "magical", "sweetheart", "fluffy", "giddy", "colorful", "lovable",
    "bouncy", "calm", "pretty", "cozy", "fresh", "gentle", "glowy", "smiley", "sparkling", "twin",
    "friendly", "graceful", "carefree", "dazzling", "snug", "dreamy", "sunny", "puffy", "jolly", "mellow"
]

cute_objects = [
    "heart", "balloon", "cupcake", "cookie", "star", "cloud", "socks", "teddy bear", "rainbow", "flower",
    "tissue box", "pillow", "blanket", "butterfly", "headband", "whisk", "paintbrush", "camera", "frame",
    "bookmark", "gloves", "pajamas", "purse", "necklace", "hat", "scarf", "bowtie", "sticker", "guitar",
    "lamp", "mug", "pencil case", "planner", "ball", "glitter", "cup", "note", "book", "bottle",
    "jewelry", "pen", "notepad", "sweets", "keychain", "coin", "bracelet", "flowerpot", "carpet",
    "diary", "mirror", "tumbler", "bottle", "lollipop", "snow globe", "painting", "clock"
]

def generate_art_prompt():
    adjective = random.choice(cute_adjectives)
    noun = random.choice(cute_nouns)
    object_ = random.choice(cute_objects)
    
    return f"a {adjective} {noun} with a {object_}"

def load_delay_time(file_path):
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:  # Check if file exists and is not empty
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                return datetime.fromisoformat(data.get('last_time', '2000-01-01T00:00:00'))  # Fallback to default date if key is missing
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_path}: {e}")
            return None
    return None

# Generalized save function for delay times
def save_delay_time(file_path):
    last_time = datetime.now()
    with open(file_path, 'w') as file:
        json.dump({"last_time": last_time.isoformat()}, file)

# Example usage for art and wake times
def load_last_art_time():
    return load_delay_time(ART_DELAY_FILE)

def save_last_art_time():
    save_delay_time(ART_DELAY_FILE)

def load_last_wake_time():
    return load_delay_time(WAKE_DELAY_FILE)

def save_last_wake_time():
    save_delay_time(WAKE_DELAY_FILE)