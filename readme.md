# Net-chan Discord Bot 🌸✨

<img src="images/net-chan.png" alt="Net-chan" width="300">

## About Net-chan

Net-chan is a kawaii Discord bot designed to handle homelab notifications with personality! Instead of receiving scattered notifications from different sources (Discord, email, text), Net-chan consolidates them into a cute, anime-inspired interface with a playful personality.

Her personality is **cute, stubborn, and proud of herself**. She responds to webhook events from your homelab scripts and makes server monitoring more enjoyable with her unique responses and interactive commands.

## Features

-   **Webhook Integration**: Responds to events like `update`, `sync`, `backup`, `unraid`, and `failure` from your network scripts
-   **Discord Webhook Handling**: Interprets and responds to existing Discord webhooks with personality
-   **User Profiles**: Remembers information about users for personalized interactions
-   **AI Art Generation**: Creates cute artwork via HuggingFace API integration
-   **Regular Affirmations**: Sends positive messages on a schedule to brighten your day
-   **Interactive Commands**: Provides a variety of fun and useful commands
-   **Server Status Monitoring**: Interprets "up" and "down" messages with appropriate responses

## Installation

### Prerequisites

-   Python 3.8+
-   `pip` (Python package manager)

### Easy Installation

Run the installer script to set up environment variables and required directories:

```bash
python installer.py
```

The installer will:

-   Guide you through setting up your `.env` file with necessary tokens and IDs
-   Create required memory directories and files
-   Set up response configurations

### Manual Installation

1.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Create Required Directories**:

    ```bash
    mkdir -p memory
    ```

3.  **Create Environment File**: Create a `.env` file with:

    ```
    DISCORD_TOKEN=your_discord_bot_token
    CHANNEL_ID=your_channel_id
    AFFIRM_ID=your_affirmations_channel_id
    WEBHOOK_BOT_ID=your_webhook_bot_id
    HUGGING_FACE_API=your_huggingface_api_key
    ```

4.  **Initialize Memory Files**:

    ```bash
    echo "{}" > ./memory/art_delay.json
    echo "{}" > ./memory/wake_delay.json
    echo "{}" > ./memory/known_users.json
    ```

## Commands

| Command | Description |
| --- | --- |
| `!help` | Shows all available commands and their descriptions |
| `!info` | Learn more about Net-chan and her personality |
| `!register` | Create a profile so Net-chan can remember you |
| `!whoami` | Check what Net-chan remembers about you |
| `!deleteme` | Delete your profile from Net-chan's memory |
| `!log` | View recent server event logs |
| `!art` | Request a cute AI-generated image (limited to once every 12 hours) |
| `!cheer` | Receive a motivational message from Net-chan |
| `!pat` | Interact with Net-chan (she may not always like it!) |
| `!music` | See what Net-chan is currently listening to |

## Configuration

### Response Configuration

Net-chan uses a `responses.json` file to store different responses for various events. Create this file with categories like:

```json
{
  "wake": [
    "Uwaaah~! (。-ω-)zzz... Oh! I'm awake! Ready to monitor your servers! ✧(≖ ◡ ≖)✧"
  ],
  "pat": [
    "H-hey! I'm busy monitoring your server! Don't distract me! (≧◡≦)"
  ],
  "affirmations": [
    "You're doing amazing today! Keep it up! (◕‿◕✿)"
  ],
  "fire": [
    "Oh no! Something's wrong with the server! I'll try to fix it! ┗(•́︿•̀｡)┛"
  ],
  "kuma": [
    "Yay! The server is back up and running! ヽ(´▽`)/"
  ],
  "unraid": [
    "Unraid is working perfectly! Your storage is safe with me! (⌐■_■)"
  ]
}
```

### Webhook Integration

Net-chan listens for webhooks on port 5000. You can send events to:

```
http://your-server-ip:5000/webhook
```

With a JSON payload like:

```json
{
  "event": "backup",
  "message": "Weekly backup completed successfully!"
}
```

## Running Net-chan

### Basic Startup

```bash
python net-chan.py
```

### Running as a Daemon (Linux)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/netchan-bot.service
```

Add the following content:

```ini
[Unit]
Description=Net-chan Discord Bot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/net-chan.py
WorkingDirectory=/path/to/project
Restart=always
User=your_user
Group=your_group

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable netchan-bot.service
sudo systemctl start netchan-bot.service
```

Check service status:

```bash
sudo systemctl status netchan-bot.service
```

## Project Structure

```
net-chan/
├── bot.py           # Main bot code
├── installer.py     # Setup script
├── requirements.txt # Python dependencies
├── .env             # Environment variables
├── responses.json   # Response templates
├── images/          # Bot images
│   ├── net-chan.png
│   ├── net-chan-angry.png
│   ├── net-chan-embarassed.png
│   └── net-chan-sleepy.png
└── memory/          # Data storage
    ├── art_delay.json
    ├── wake_delay.json
    └── known_users.json
```

## Customization

-   **Add More Responses**: Edit the `responses.json` file to add more response variations
-   **New Commands**: Extend `net-chan.py` to add custom commands
-   **Webhook Events**: Create new event types in `responses.json` for additional webhook integrations
-   **Appearance**: Add more images to the `images/` directory for different emotional states

## Contributing

Contributions are welcome! Feel free to:

-   Submit pull requests
-   Open issues for bugs or feature requests
-   Share ideas for new commands or integrations

## Future Plans

-   Add more interactive commands
-   Expand webhook integration capabilities
-   Improve AI art generation options
-   Add voice channel interactions
-   Create a dashboard for viewing server status

## License

This project is licensed under the MIT License - see the LICENSE file for details.
