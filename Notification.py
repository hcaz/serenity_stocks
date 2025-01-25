from pydantic import BaseModel

from User import User
from bson import ObjectId

class NotificationReply(BaseModel):
    sender: str
    message: str
    timestamp: float

# Pydantic model for notification data
class Notification(BaseModel):
    _id: ObjectId
    sender: User
    recipient: User
    subject: str
    message: str
    read_by_user: bool
    read_by_system: bool
    replies: list[NotificationReply]
    timestamp: float
