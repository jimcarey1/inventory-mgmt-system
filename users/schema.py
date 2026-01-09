from pydantic import BaseModel, EmailStr
from datetime import datetime

from .tables import User

class UserRegisterDTO(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserLoginDTO(BaseModel):
    username: str
    password: str

class UserDTO(BaseModel):
    id:int
    username:str
    email:str
    role:str

    @property
    def is_admin(self)->bool:
        return self.role == 'admin'
