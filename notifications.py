import json
import time
from fastapi import HTTPException
from Notification import Notification
from User import User
from AtlasClient import getClient
from bson import ObjectId

user_collection = getClient().get_collection("serenity_stocks", "users")
notification_collection = getClient().get_collection("serenity_stocks", "notifications")

def get_notifications(email: str):
    """
    Fetch a list of notification documents.
    """

    existing_user = user_collection.find_one({"email": email})

    if existing_user:
        existing_user["last_seen"] = time.time()
        user_collection.replace_one({"email": email}, existing_user)

        notifications = []
        cursor = notification_collection.find({'recipient': email})  # Fetch all documents
        cursor = list(cursor)
        for document in cursor:
            sending_user = user_collection.find_one({"email": document['sender']})
            if sending_user:
                document['recipient'] = existing_user
                document['sender'] = sending_user
                notifications.append(Notification(**document))
        return notifications
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
def read_notification(id: ObjectId):
    """
    Fetch a list of notification documents.
    """

    existing_notification = notification_collection.find_one({"_id": id})
    if existing_notification:
        existing_notification["read_by_user"] = True
        notification_collection.replace_one({"_id": id}, existing_notification)
        sending_user = user_collection.find_one({"email": existing_notification['sender']})
        recipient_user = user_collection.find_one({"email": existing_notification['recipient']})
        if sending_user and recipient_user:
            existing_notification['recipient'] = recipient_user
            existing_notification['sender'] = sending_user

            return Notification(**existing_notification)
        else:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        raise HTTPException(status_code=404, detail="Notification not found")