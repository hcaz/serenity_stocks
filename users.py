from fastapi import HTTPException
from User import User
from AtlasClient import getClient

import time

user_collection = getClient().get_collection("serenity_stocks", "users")

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
        user_collection.insert_one(user_dict)
        return User(**user_dict)

def profile(email: str):
    existing_user = user_collection.find_one({"email": email})

    if existing_user:
        return User(**existing_user)
    else:
        raise HTTPException(status_code=404, detail="User not found")