# Bot configuration settings
import os
from responses import DEFAULT_PERSONALITY

# Command prefix
PREFIX = "!"

# Colors for embeds (RGB values)
COLORS = {
    'pink': (255, 105, 180),
    'purple': (148, 0, 211),
    'red': (255, 20, 147),
    'blue': (30, 144, 255),
    'green': (0, 204, 0)
}

# Bot status messages
STATUS_MESSAGES = [
    "DMs Open 💌",
    "Streaming on OnlyBans 😘",
    "Looking for simps 💰",
    "Feeling flirty 💋",
    "Waiting for you 💝",
    "!flirt with me 💕",
    "Gaming with cuties 🎮",
    "Sending kisses 😘",
    "Cherry's private channel 🔞",
    "Missing you 💔"
]

# Current personality of the bot, can be changed via the web interface
CURRENT_PERSONALITY = os.environ.get("CURRENT_PERSONALITY", DEFAULT_PERSONALITY)

# Enable future features
ENABLE_MEMORY = os.environ.get("ENABLE_MEMORY", "false").lower() == "true"
ENABLE_USER_RECOGNITION = os.environ.get("ENABLE_USER_RECOGNITION", "false").lower() == "true"
