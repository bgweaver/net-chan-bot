# Net-chan Discord Bot

<img src="images/net-chan.png" alt="Net-chan" width="300">

My homelab has been a bit scattered, and I had been getting notifications from Discord, email, and text from different sources with updates. I wanted a Discord bot to handle all of my notifications.  

Previously, I had flavored my bot as a servo-skull from 40k, but that got stale. I've been listening to uwu-underground and appreciating their style, so I decided to ask ChatGPT for a cute anime server girl I could give a personality. That makes the messages a lot more fun to receive!  

Her personality is **cute, stubborn, and proud of herself**. After I finished with the homelab updates, I worked on some commands to expand her personality and make it so I could interact with her.  

I relied more heavily on ChatGPT than I have on other projects since I was mostly playing around and having fun, but I think I picked up enough from tweaking and reading the docs to build other simple bots. It's a bit scattered, so I'd appreciate any advice or update ideas!

## Features

- Responds to webhook events like `update`, `sync`, `backup`, `unraid`, and `failure` from scripts on my network.
- Personalizes webhook events and shares them in the Discord chat.
- Responds to Discord webhook updates (for those I haven’t integrated into her yet) and makes snarky responses about how she could make them cuter.
- Responds to a few basic commands with response banks to add personality and variety.
- Can make API requests to HuggingFace to generate cute art.


Installation
------------

### Prerequisites

Ensure you have the following installed on your system:

-   Python 3.8+

-   `pip` (Python package manager)

### Dependencies

Install the required dependencies using pip:

```
pip install -r requirements.txt
```

#### Required Python Packages

-   `discord.py`

-   `Flask`

-   `python-dotenv`

-   `Pillow`

-   `requests`

Setup
-----

### Environment Variables

Create a `.env` file in the project directory with the following variables:

```
DISCORD_TOKEN=your_discord_bot_token
CHANNEL_ID=your_channel_id
AFFIRM_ID=your_affirmations_channel_id
WEBHOOK_BOT_ID=your_webhook_bot_id
HUGGING_FACE_API=your_huggingface_api_key
```

### Running the Bot

Start the bot with:

```
python bot.py
```

Commands
--------

| Command | Description |
| `!commands` | Displays a list of available commands |
| `!pat` | Responds with a playful reaction |
| `!cheer` | Sends a motivational message |
| `!art` | Generates and sends AI-generated artwork (limited to once every 12 hours) |
| `!info` | Provides details about Net-chan |

Running as a Daemon (Optional)
------------------------------

If you want to run Net-chan as a system service on Linux, create a systemd service file:

```
sudo nano /etc/systemd/system/netchan-bot.service
```

Add the following content:

```
[Unit]
Description=Net-chan Discord Bot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/bot.py
WorkingDirectory=/path/to/project
Restart=always
User=your_user
Group=your_group

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:

```
sudo systemctl enable netchan-bot.service
sudo systemctl start netchan-bot.service
```

To stop it from running automatically:

```
sudo systemctl disable netchan-bot.service
```

Contributing
------------

If you'd like to contribute, feel free to submit a pull request or open an issue.

License
-------

This project is licensed under the MIT License.