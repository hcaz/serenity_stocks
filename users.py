from fastapi import HTTPException
from User import User
from AtlasClient import getClient

import time
import random

user_collection = getClient().get_collection("serenity_stocks", "users")
notification_collection = getClient().get_collection("serenity_stocks", "notifications")

slogans = [
    "Play the market. Play dirty.",
    "Risk everything. Regret nothing."
    "The only limit is your morality.",
    "The market doesn't care about your conscience.",
    "Success at all costs. Morality is optional.",
    "We'll handle the ethics. You handle the profits.",
]

def login(email: str):
    existing_user = user_collection.find_one({"email": email})

    if existing_user:
        existing_user["last_seen"] = time.time()
        user_collection.replace_one({"email": email}, existing_user)

        return User(**existing_user)
    else:
        user_dict = {}
        user_dict['email'] = email
        user_dict['name'] = 'Nick Leeson'
        user_dict['job_role'] = 'Junior Stock Trader'
        user_dict["last_seen"] = time.time()
        user_dict["joined"] = time.time()
        user_dict["budget_remaining"] = 1000 * 100
        user_dict["balance"] = 100 * 100
        result = user_collection.insert_one(user_dict)

        notification_dict = {}
        notification_dict['sender'] = email
        notification_dict['recipient'] = email
        notification_dict['subject'] = 'Welcome to Serenity Stocks'
        notification_dict['message'] = """Hi there,

Welcome to Serenity Stocks! We're thrilled to have you join our team.

We know you're eager to get started, and we'll be sending you more information about your role and what to expect very shortly.

But first, we'd love to get to know you a little better.  Could you reply to this email and let us know your name?

We're excited to have you on board and can't wait to see what you'll achieve here.

Best regards,
---

"""+random.choice(slogans)
        notification_dict['read_by_user'] = False
        notification_dict['read_by_system'] = False
        notification_dict['replies'] = []
        notification_dict['timestamp'] = time.time()
        notification_collection.insert_one(notification_dict)

        return User(**user_dict)

def profile(email: str):
    existing_user = user_collection.find_one({"email": email})

    if existing_user:
        return User(**existing_user)
    else:
        raise HTTPException(status_code=404, detail="User not found")