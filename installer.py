#!/usr/bin/env python3
import os
import json
import subprocess
import sys
import venv

def print_banner():
    print("""
    ✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨
    ✨                                                ✨
    ✨   Net-chan Discord Bot Installer  (≧◡≦)       ✨
    ✨                                                ✨
    ✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨
    """)

def setup_virtual_environment():
    print("👾 Setting up virtual environment... (｡•́︿•̀｡)")
    
    venv_dir = "netchan-env"
    
    # Check if virtual environment already exists
    if os.path.exists(venv_dir):
        print(f"✓ Virtual environment '{venv_dir}' already exists")
    else:
        print(f"📦 Creating virtual environment in '{venv_dir}'...")
        try:
            venv.create(venv_dir, with_pip=True)
            print(f"✅ Virtual environment created successfully in '{venv_dir}'!")
        except Exception as e:
            print(f"❌ Failed to create virtual environment: {str(e)}")
            return False
    
    # Determine path to pip in the virtual environment
    if os.name == 'nt':  # Windows
        pip_path = os.path.join(venv_dir, 'Scripts', 'pip')
        python_path = os.path.join(venv_dir, 'Scripts', 'python')
    else:  # Unix/Linux/MacOS
        pip_path = os.path.join(venv_dir, 'bin', 'pip')
        python_path = os.path.join(venv_dir, 'bin', 'python')
    
    # Return paths for later use
    return True, pip_path, python_path, venv_dir

def install_dependencies(pip_path):
    print("\n👾 Installing dependencies in virtual environment... This might take a moment (｡•́︿•̀｡)")
    
    # Check if pip is available in the virtual environment
    try:
        subprocess.check_call([pip_path, "--version"])
    except subprocess.CalledProcessError:
        print(f"❌ Error: pip is not available in the virtual environment at {pip_path}")
        return False
    
    # List of required packages
    requirements = [
        "discord.py==2.3.2",
        "Flask==2.3.3",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "Pillow==10.1.0",
        "better-profanity==0.7.0"
    ]
    
    # Install each package
    for package in requirements:
        print(f"📦 Installing {package.split('==')[0]}...")
        try:
            subprocess.check_call([pip_path, "install", package])
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}. Please try installing it manually.")
            return False
    
    print("✅ All dependencies installed successfully! (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧")
    return True

def create_directories():
    print("\n👾 Creating necessary directories... (๑˃̵ᴗ˂̵)")
    
    # Create memory directory
    if not os.path.exists("memory"):
        os.makedirs("memory")
        print("✅ Created 'memory' directory")
    else:
        print("✓ 'memory' directory already exists")
    
    # Create images directory if it doesn't exist
    if not os.path.exists("images"):
        os.makedirs("images")
        print("✅ Created 'images' directory")
        print("ℹ️ Don't forget to add Net-chan's images to the 'images' directory!")
    else:
        print("✓ 'images' directory already exists")
    
    return True

def initialize_memory_files():
    print("\n👾 Initializing memory files... (｡•̀ᴗ•́｡)✧")
    
    # Initialize memory files with empty JSON objects
    memory_files = [
        "memory/art_delay.json",
        "memory/wake_delay.json",
        "memory/known_users.json"
    ]
    
    for file_path in memory_files:
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            with open(file_path, "w") as f:
                f.write("{}")
            print(f"✅ Initialized {file_path}")
        else:
            print(f"✓ {file_path} already exists")
    
    return True

def create_sample_responses():
    print("\n👾 Creating sample responses file... (≧◡≦)")
    
    if os.path.exists("responses.json") and os.path.getsize("responses.json") > 0:
        print("✓ responses.json already exists")
        return True
    
    sample_responses = {
        "wake": [
            "Uwaaah~! (。-ω-)zzz... Oh! I'm awake! Ready to monitor your servers! ✧(≖ ◡ ≖)✧",
            "Good morning, everyone! Net-chan is online and ready to help! (◕‿◕✿)"
        ],
        "pat": [
            "H-hey! I'm busy monitoring your server! Don't distract me! (≧◡≦)",
            "Nyaa~! That tickles! But I need to focus on my important server tasks! (｡•́︿•̀｡)"
        ],
        "pat_annoyed": [
            "S-stop that! I'm trying to work! (╯︵╰,)",
            "No more pats! I'm not a pet! I'm a sophisticated server manager! ヽ(≧Д≦)ノ"
        ],
        "affirmations": [
            "You're doing amazing today! Keep it up! (◕‿◕✿)",
            "Remember that you're capable of incredible things! ✨(｡♥‿♥｡)✨"
        ],
        "fire": [
            "Oh no! Something's wrong with the server! I'll try to fix it! ┗(•́︿•̀｡)┛",
            "AHHH! Server alert! Don't panic! Net-chan is on the case! (ノಠ益ಠ)ノ彡┻━┻"
        ],
        "kuma": [
            "Yay! The server is back up and running! ヽ(´▽`)/",
            "Everything is green again! Great job, team! (≧◡≦)"
        ],
        "unraid": [
            "Unraid is working perfectly! Your storage is safe with me! (⌐■_■)",
            "Checking on Unraid... everything looks good! No need to worry! (´｡• ᵕ •｡`)"
        ]
    }
    
    with open("responses.json", "w") as f:
        json.dump(sample_responses, f, indent=2)
    
    print("✅ Created sample responses.json")
    return True

def setup_env_file():
    print("\n👾 Setting up environment variables... (/◕ヮ◕)/")
    
    if os.path.exists(".env") and os.path.getsize(".env") > 0:
        overwrite = input("⚠️ .env file already exists. Do you want to overwrite it? (y/n): ")
        if overwrite.lower() != 'y':
            print("✓ Keeping existing .env file")
            return True
    
    print("\nℹ️ Let's set up your .env file with the necessary credentials")
    print("ℹ️ If you don't have some of these values yet, you can leave them blank and fill them in later")
    
    discord_token = input("\n🔑 Discord Bot Token (from Discord Developer Portal): ")
    channel_id = input("🆔 Main Channel ID (for receiving webhook notifications): ")
    affirm_id = input("🆔 Affirmations Channel ID (for sending positive messages): ")
    webhook_bot_id = input("🆔 Webhook Bot ID (if using a webhook integration): ")
    huggingface_api = input("🔑 HuggingFace API Key (for art generation): ")
    
    env_content = f"""DISCORD_TOKEN={discord_token}
CHANNEL_ID={channel_id}
AFFIRM_ID={affirm_id}
WEBHOOK_BOT_ID={webhook_bot_id}
HUGGING_FACE_API={huggingface_api}
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Created .env file")
    return True

def create_activation_script(venv_dir, python_path):
    print("\n👾 Creating activation scripts... (≧◡≦)")
    
    if os.name == 'nt':  # Windows
        with open("start_netchan.bat", "w") as f:
            f.write(f'@echo off\necho Starting Net-chan...\n"{python_path}" bot.py\npause')
        print("✅ Created start_netchan.bat")
    else:  # Unix/Linux/MacOS
        with open("start_netchan.sh", "w") as f:
            f.write(f'#!/bin/bash\necho "Starting Net-chan..."\n{python_path} bot.py')
        # Make the file executable
        os.chmod("start_netchan.sh", 0o755)
        print("✅ Created start_netchan.sh")
    
    return True

def main():
    print_banner()
    
    print("Net-chan is ready to be installed on your system! (◕‿◕✿)")
    print("This installer will help you set up everything you need to run Net-chan.\n")
    
    proceed = input("Do you want to proceed with the installation? (y/n): ")
    if proceed.lower() != 'y':
        print("\nInstallation cancelled. Goodbye! (｡•́︿•̀｡)")
        return
    
    # Setup virtual environment first
    venv_result = setup_virtual_environment()
    if not venv_result[0]:
        print("\n❌ Failed during: Setting up virtual environment")
        print("Please fix the issues and try again.")
        return
    
    pip_path, python_path, venv_dir = venv_result[1:]
    
    steps = [
        ("Installing dependencies", lambda: install_dependencies(pip_path)),
        ("Creating directories", create_directories),
        ("Initializing memory files", initialize_memory_files),
        ("Creating sample responses", create_sample_responses),
        ("Setting up environment variables", setup_env_file),
        ("Creating activation scripts", lambda: create_activation_script(venv_dir, python_path))
    ]
    
    for step_name, step_function in steps:
        print(f"\n=== {step_name} ===")
        if not step_function():
            print(f"\n❌ Failed during: {step_name}")
            print("Please fix the issues and try again.")
            return
    
    print("\n✨✨✨ Installation complete! ✨✨✨")
    print(f"""
    Net-chan is now ready to help monitor your servers! (≧◡≦)
    
    To start Net-chan, use:
        {os.name == 'nt' and '.\\start_netchan.bat' or './start_netchan.sh'}
    
    (This will use the Python from your virtual environment)
    
    Don't forget to:
    1. Review and customize your responses.json file
    2. Add Net-chan's images to the 'images' directory
    3. Complete any missing values in your .env file
    
    Your virtual environment is in the '{venv_dir}' directory.
    
    Have fun with your new kawaii server assistant! ヽ(´▽`)/
    """)

if __name__ == "__main__":
    main()