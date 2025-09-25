import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debug: Print environment variables for troubleshooting
print("🔍 Debug - Environment Variables:")
print(f"BOT_TOKEN: {'SET' if os.getenv('BOT_TOKEN') else 'NOT SET'}")
print(f"API_ID: {os.getenv('API_ID', 'NOT SET')}")
print(f"API_HASH: {'SET' if os.getenv('API_HASH') else 'NOT SET'}")
print(f"AUTHORIZED_USERS: {os.getenv('AUTHORIZED_USERS', 'NOT SET')}")

# Telegram API credentials
API_ID = int(os.getenv('API_ID', '2040'))
API_HASH = os.getenv('API_HASH', 'b18441a1ff607e10a989891a5462e627')
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Read from environment for security

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN is not set in environment variables!")
    print("Available environment variables:")
    for key in sorted(os.environ.keys()):
        if 'TOKEN' in key or 'API' in key or 'BOT' in key:
            print(f"  {key}: {'SET' if os.environ[key] else 'EMPTY'}")
else:
    print(f"✅ BOT_TOKEN loaded successfully: {BOT_TOKEN[:10]}...")

# Optional: Use a Local Bot API server (to send files up to 2GB)
# If you run a local telegram-bot-api server, set these in your .env:
# BOT_API_BASE_URL=http://<host>:8081/bot
# BOT_API_BASE_FILE_URL=http://<host>:8081/file/bot
BOT_API_BASE_URL = os.getenv('BOT_API_BASE_URL')
BOT_API_BASE_FILE_URL = os.getenv('BOT_API_BASE_FILE_URL')

# Optional: Free large-file workaround without Local Bot API
# Generate a Pyrogram session string locally and set TG_SESSION_STRING,
# and create a private channel, add both your user and the bot as admins,
# then set its ID as BRIDGE_CHANNEL_ID.
TG_SESSION_STRING = os.getenv('TG_SESSION_STRING')
BRIDGE_CHANNEL_ID = int(os.getenv('BRIDGE_CHANNEL_ID', '0'))

# Authorization settings
_auth_users_raw = os.getenv('AUTHORIZED_USERS', '').strip()
AUTHORIZED_USERS = set()
if _auth_users_raw:
    try:
        AUTHORIZED_USERS = {int(x.strip()) for x in _auth_users_raw.split(',') if x.strip()}
    except Exception:
        # Ignore parse errors; will fall back to defaults in bot.py
        AUTHORIZED_USERS = set()

ALLOW_ALL = os.getenv('ALLOW_ALL', 'false').lower() in {'1', 'true', 'yes', 'on'}
