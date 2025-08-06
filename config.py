import os
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

ADMIN_ID = os.getenv("ADMIN_ID")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID environment variable not set")
ADMIN_ID = int(ADMIN_ID)

PREMIUM_USERS = json.loads(os.getenv("PREMIUM_USERS", "[]"))
