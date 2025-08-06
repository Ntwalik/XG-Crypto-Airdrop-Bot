import json
import threading

DB_FILE = "database.json"
AIRDROP_FILE = "airdrops.json"
lock = threading.Lock()

def load_data():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": [], "referrals": {}}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_user(user_id, referrer_id=None):
    with lock:
        data = load_data()
        if user_id not in data["users"]:
            data["users"].append(user_id)
            # Add referral if valid and not self-referral
            if referrer_id and str(referrer_id) != str(user_id):
                data.setdefault("referrals", {}).setdefault(str(referrer_id), []).append(user_id)
            save_data(data)

def is_premium_user(user_id):
    data = load_data()
    referred = data.get("referrals", {}).get(str(user_id), [])
    # Premium if user is admin or has referred 5 or more users
    return len(referred) >= 5 or user_id in [8438037540]  # Replace admin ID with your own

def get_referral_count(user_id):
    data = load_data()
    return len(data.get("referrals", {}).get(str(user_id), []))

def get_referral_link(user_id):
    # Replace 'YourBotUsername' with your actual Telegram bot username
    return f"https://t.me/tlxke?start={user_id}"

def get_airdrops(premium=False):
    try:
        with open(AIRDROP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return f"⚠️ Failed to load airdrop list: {e}"

    message = "🪂 *Free Airdrops:*\n\n"
    for drop in data[:3]:  # First 3 airdrops for all users
        message += f"• *{drop['title']}*\n{drop['link']}\n{drop['description'][:100]}...\n\n"

    if premium:
        message += "\n💎 *Premium Airdrops:*\n\n"
        for drop in data[3:6]:  # Next 3 airdrops for premium users
            message += f"• *{drop['title']}*\n{drop['link']}\n{drop['description'][:100]}...\n\n"

    return message
