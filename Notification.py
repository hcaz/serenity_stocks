from pydantic import BaseModel

from User import User

# Pydantic model for notification data
class Notification(BaseModel):
    sender: User
    recipient: User
    subject: str
    message: str
    read: bool
    timestamp: float
