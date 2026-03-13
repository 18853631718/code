from typing import List, Optional
from datetime import datetime

class SessionCreateRequest:
    def __init__(self, name: str, owner: str):
        self.name = name
        self.owner = owner

class SessionJoinRequest:
    def __init__(self, user: str):
        self.user = user

class CommentCreateRequest:
    def __init__(self, author: str, content: str, line_number: Optional[int]):
        self.author = author
        self.content = content
        self.line_number = line_number

class SessionResponse:
    def __init__(self, id: int, name: str, owner: str, status: str, participants: List[str], created_at: datetime):
        self.id = id
        self.name = name
        self.owner = owner
        self.status = status
        self.participants = participants
        self.created_at = created_at

class CommentResponse:
    def __init__(self, id: int, session_id: int, author: str, content: str, line_number: Optional[int], created_at: datetime):
        self.id = id
        self.session_id = session_id
        self.author = author
        self.content = content
        self.line_number = line_number
        self.created_at = created_at
