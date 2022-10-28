from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, conint

class BasePost(BaseModel):
    title: str
    content: str
    publisher: bool = True
    
class PostCreate(BasePost):
    pass

class UserOut(BaseModel):
    id: int
    email: EmailStr
    create_at: datetime

    class Config:
        orm_mode = True

class Post(BasePost):
    id: int
    create_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        orm_mode = True

class PostVote(BaseModel):
    Post: Post
    votes: int

    class Config:
        orm_mode = True
 
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(UserCreate):
    pass
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id : Optional[str] = None

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)