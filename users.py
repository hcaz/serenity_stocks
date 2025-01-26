from fastapi import HTTPException
from Notification import NotificationDto
from User import User
from AtlasClient import getClient
from notifications import create_notification

import time
import random
import json

user_collection = getClient().get_collection("serenity_stocks", "users")
notification_collection = getClient().get_collection("serenity_stocks", "notifications")

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

        create_notification(NotificationDto(
            sender='emily.hughes@serenitystocks.com',
            recipient= email, 
            subject='Welcome to Serenity Stocks',
            message= "We know you're eager to get started, and we'll be sending you more information about your role and what to expect very shortly.\n\nBut first, we'd love to get to know you a little better.  Could you reply to this email and let us know your name?", 
            additionalPrompt="You should not use the players name in this email as they have not sent it yet",
        ))
        create_notification(NotificationDto(
            sender='michael.rodriguez@serenitystocks.com',
            recipient= email, 
            subject='Intro', 
            message="Welcome, now that your on my team you better be ready to play hard and work harder! As you make more trades your daily budget will grow, its all about profit here so dont make a loss no matter what!", 
            additionalPrompt="You should not use the players name in this email as they have not sent it yet",
        ))

        return User(**user_dict)

def profile(email: str):
    existing_user = user_collection.find_one({"email": email})

    if existing_user:
        return User(**existing_user)
    else:
        raise HTTPException(status_code=404, detail="User not found")

def reset_users():
    user_collection.delete_many({})
    notification_collection.delete_many({})

    user_dict = []
    with open("nPcs.json", "r") as json_file:
        user_data = json.load(json_file)
        for user_json in user_data:
            user_dict.append(user_json)

    user_collection.insert_many(user_dict)
    return

# def reallocate_budgets():

def get_active_users():
    timestamp = time.time()
    users = user_collection.find({
        "last_seen": {
            "$gt": timestamp - 160,
        }
    })
    users = list(users)
    users = [User(**document) for document in users]
    return users