from pydantic import BaseModel

class UserBase(BaseModel):
    email : str
    password : str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id : int

    class Config:
        orm_mode = True

class NoteBase(BaseModel):
    title : str
    content : str

class NoteCreate(NoteBase):
    pass

class Note(NoteBase):
    id : int
    owner_id : int

    class Config:
        orm_mode = True