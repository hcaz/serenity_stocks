from pydantic import BaseModel
from typing import Optional

from models.User import User

class NotificationReply(BaseModel):
    sender: str
    message: str
    Optional[float]

# Pydantic model for notification data
class Notification(BaseModel):
    id: Optional[str] = None
    sender: User
    recipient: User
    subject: str
    message: str
    read_by_user: Optional[bool] = False
    read_by_system: Optional[bool] = False
    replies: Optional[list[NotificationReply]] = []
    timestamp: Optional[float]

class NotificationDto(BaseModel):
    sender: str
    recipient: str
    subject: str
    message: str
    additionalPrompt: str = ""