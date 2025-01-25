from pydantic import BaseModel

from User import User

class NotificationReply(BaseModel):
    by: str
    message: str
    timestamp: float

# Pydantic model for notification data
class Notification(BaseModel):
    sender: User
    recipient: User
    subject: str
    message: str
    read_by_user: bool
    read_by_system: bool
    replies: list[NotificationReply]
    timestamp: float
