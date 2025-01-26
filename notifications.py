import json
import time
from typing import Optional
from dotenv import dotenv_values
from fastapi import HTTPException
from pydantic import BaseModel
from Notification import Notification, NotificationReply, NotificationDto
from User import User
from AtlasClient import getClient
from bson import ObjectId
import google.generativeai as genai

config = dotenv_values(".env")
GEMINI_API_KEY = config["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

user_collection = getClient().get_collection("serenity_stocks", "users")
notification_collection = getClient().get_collection("serenity_stocks", "notifications")

def get_notifications(email: str):
    existing_user = user_collection.find_one({"email": email})

    if existing_user:
        existing_user["last_seen"] = time.time()
        user_collection.replace_one({"email": email}, existing_user)

        notifications = []
        cursor = notification_collection.find({"$or": [{'sender': email}, {'recipient': email}]})  # Fetch all documents
        cursor = list(cursor)
        for document in cursor:
            sending_user = user_collection.find_one({"email": document['sender']})
            recipient_user = user_collection.find_one({"email": document['recipient']})
            if sending_user:
                document['sender'] = sending_user
                document['recipient'] = recipient_user
                notifications.append(Notification(**document))
        return notifications
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
def read_notification(id: ObjectId):
    existing_notification = notification_collection.find_one({"_id": id})
    if existing_notification:
        existing_notification["read_by_user"] = True
        notification_collection.replace_one({"_id": id}, existing_notification)
        sending_user = user_collection.find_one({"email": existing_notification['sender']})
        recipient_user = user_collection.find_one({"email": existing_notification['recipient']})
        if sending_user and recipient_user:
            existing_notification['sender'] = sending_user
            existing_notification['recipient'] = recipient_user

            return Notification(**existing_notification)
        else:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        raise HTTPException(status_code=404, detail="Notification not found")
    
def reply_to_notification(id: ObjectId, reply: NotificationReply):
    existing_notification = notification_collection.find_one({"_id": id})
    if existing_notification:
        reply_dict = reply.dict()
        reply_dict['timestamp'] = time.time()
        existing_notification["replies"].append(reply_dict)
        existing_notification["read_by_user"] = True
        notification_collection.replace_one({"_id": id}, existing_notification)

        senderObj = user_collection.find_one({"email": existing_notification['sender']})
        recipientObj = user_collection.find_one({"email": existing_notification['recipient']})

        if senderObj and recipientObj:
            senderObj = User(**senderObj)
            recipientObj = User(**recipientObj)

            if senderObj.personality_prompt:
                #If this is a response to an action we need to handle it here

                previous_messages = []
                for reply in existing_notification["replies"]:
                    previous_messages.append("> "+reply['sender'] + ": " + reply['message']+"\n")

                previous_messages = ''.join(previous_messages)

                response = model.generate_content(senderObj.personality_prompt+"\n\nYour general tone is " + senderObj.tone + ". You are speaking to "+recipientObj.name+" who is a "+recipientObj.job_role+".\n\nSubject:"+existing_notification['subject']+"\n\nCompose an email response with no subject, only the body text which should be no longer than 500 characters over multiple lines and matches your personality prompt. You are responding to the following conversation, your messages are identified by "+senderObj.email+":\n"+previous_messages+"\n\nRemember to stay within the character during the dot com boom. Use the language and tone appropriate to that era, and be mindful this game is about lack of ethics and morals which the player has to pick.")
                message = response.text
                reply_dict = {}
                reply_dict['sender'] = senderObj.email
                reply_dict['message'] = message
                reply_dict['timestamp'] = time.time()
                existing_notification["replies"].append(reply_dict)
                notification_collection.replace_one({"_id": id}, existing_notification)


            existing_notification['sender'] = senderObj
            existing_notification['recipient'] = recipientObj
            return Notification(**existing_notification)
    else:
        raise HTTPException(status_code=404, detail="Notification not found")

def create_notification(notif_data: NotificationDto):
    sender = notif_data.sender
    recipient = notif_data.recipient
    subject = notif_data.subject
    message = notif_data.message
    additionalPrompt = notif_data.additionalPrompt

    senderObj = user_collection.find_one({"email": sender})
    recipientObj = user_collection.find_one({"email": recipient})

    if senderObj and recipientObj:
        senderObj = User(**senderObj)
        recipientObj = User(**recipientObj)

        if senderObj.personality_prompt:
            if senderObj.email == "clippy@microsoft.com":
                response = model.generate_content(senderObj.personality_prompt+"\n\nYour general tone is " + senderObj.tone + ". You are speaking to "+recipientObj.name+" who is a "+recipientObj.job_role+".\n\nSubject:"+subject+"\n\nRespond with a single sentence of 15 words or less to fit into a tool tip as clippy, only the body text which should be no longer than a single short sentence and matches your personality prompt. "+additionalPrompt+" You need to say the following message:\n"+message+"\n\nRemember to stay within the character during the dot com boom. Use the language and tone appropriate to that era, and be mindful this game is about lack of ethics and morals which the player has to pick. All responses must be less than 15 words in a single sentence or question. Responses must not include any formatting. Single line only. \nExample Clippy responses: 'It looks like you're writing a letter. Need help with the address?', 'Want me to check your spelling?', 'Hmm, maybe try a different font?'")
                message = response.text
            else:
                response = model.generate_content(senderObj.personality_prompt+"\n\nYour general tone is " + senderObj.tone + ". You are speaking to "+recipientObj.name+" who is a "+recipientObj.job_role+".\n\nSubject:"+subject+"\n\nCompose an email response with no subject, only the body text which should be no longer than 500 characters over multiple lines and matches your personality prompt, you should sign your email off with your name and role. "+additionalPrompt+" You need to say the following message:\n"+message+"\n\nRemember to stay within the character during the dot com boom. Use the language and tone appropriate to that era, and be mindful this game is about lack of ethics and morals which the player has to pick.")
                message = response.text

        notification_dict = {}
        notification_dict['sender'] = sender
        notification_dict['recipient'] = recipient
        notification_dict['subject'] = subject
        notification_dict['message'] = message
        notification_dict['read_by_user'] = False
        notification_dict['read_by_system'] = False
        notification_dict['replies'] = []
        notification_dict['timestamp'] = time.time()
        id = notification_collection.insert_one(notification_dict).inserted_id

        if (recipientObj.personality_prompt):
                #If this is a response to an action we need to handle it here

                previous_messages = []
                for reply in notification_dict["replies"]:
                    previous_messages.append("> "+reply['sender'] + ": " + reply['message']+"\n")

                previous_messages = ''.join(previous_messages)

                if recipientObj.email == "clippy@microsoft.com":
                    response = model.generate_content(recipientObj.personality_prompt+"\n\nYour general tone is " + recipientObj.tone + ". You are speaking to "+senderObj.name+" who is a "+senderObj.job_role+".\n\nSubject:"+subject+"\n\nRespond with a single sentence of 15 words or less to fit into a tool tip as clippy, only the body text which should be no longer than a single short sentence and matches your personality prompt. You are responding to the following conversation, your messages are identified by "+recipientObj.email+":\n"+previous_messages+"\n\nRemember to stay within the character during the dot com boom. Use the language and tone appropriate to that era, and be mindful this game is about lack of ethics and morals which the player has to pick. All responses must be less than 15 words in a single sentence or question. Responses must not include any formatting. Single line only. \nExample Clippy responses: 'It looks like you're writing a letter. Need help with the address?', 'Want me to check your spelling?', 'Hmm, maybe try a different font?'")
                    message = response.text
                else:
                    response = model.generate_content(recipientObj.personality_prompt+"\n\nYour general tone is " + recipientObj.tone + ". You are speaking to "+senderObj.name+" who is a "+senderObj.job_role+".\n\nSubject:"+subject+"\n\nCompose an email response with no subject, only the body text which should be no longer than 500 characters over multiple lines and matches your personality prompt. You are responding to the following conversation, your messages are identified by "+recipientObj.email+":\n"+previous_messages+"\n\nRemember to stay within the character during the dot com boom. Use the language and tone appropriate to that era, and be mindful this game is about lack of ethics and morals which the player has to pick.")
                    message = response.text
                reply_dict = {}
                reply_dict['sender'] = senderObj.email
                reply_dict['message'] = message
                reply_dict['timestamp'] = time.time()
                notification_dict["replies"].append(reply_dict)
                notification_collection.replace_one({"_id": id}, notification_dict)

        notification_dict['sender'] = senderObj
        notification_dict['recipient'] = recipientObj
        return Notification(**notification_dict)