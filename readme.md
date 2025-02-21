Net-chan Discord Bot
====================
![Net-chan](images/net-chan.png)

Net-chan is a Discord bot designed to interact with users in a friendly and engaging way. It can respond to messages, generate artwork, send affirmations, and integrate with a Flask web server for additional functionality.

Features
--------

-   Responds to user commands with cheerful messages

-   Sends daily affirmations at random intervals

-   Generates AI-powered artwork

-   Responds to webhooks from a homelab server

-   Greets users when it becomes active

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