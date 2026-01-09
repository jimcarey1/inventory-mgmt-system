from litestar import Controller, get, post, Request, Response
from litestar.response import Template
from litestar.di import Provide
from litestar.status_codes import HTTP_200_OK
from litestar.exceptions import NotAuthorizedException

from typing import Any, Optional

from .tables import User
from .schema import UserDTO, UserLoginDTO, UserRegisterDTO
from utils.hash_util import hash_password, verify_password


async def get_current_user(request: Request) -> User:
    if not request.user:
        raise NotAuthorizedException("Not authenticated")
    return request.user

class UserController(Controller):
    path = '/account'

    @get('/register')
    async def register(self)->Template:
        return Template('/user/register.html')
    
    @post('/register-user')
    async def register_user(self, data:UserRegisterDTO, request:Request[Any, Any, Any])->UserDTO:
        try:
            hashed_password = await hash_password(data.password)
            user = User(username=data.username, email=data.email, password=hashed_password)
            await User.insert(user)
            await user.refresh(columns=['id'])
            return user
        except Exception as e:
            print(e)
            pass
    
    @get('/login')
    async def login(self)->Template:
        return Template('/user/login.html') 
    
    @post("/login-user")
    async def login_user(self, data: UserLoginDTO, request: Request[Any, Any, Any])->UserDTO:
        try:
            user = await User.objects().get(User.username == data.username)
        except Exception as e:
            pass

        if not user:
            raise NotAuthorizedException("invalid credentials")
        
        ok = await verify_password(data.password, user.password)
        if not ok:
            raise NotAuthorizedException("invalid credentials")
        request.set_session({"user_id": str(user.id)})
        return {"message": "success"}
    
    @post("/logout")
    async def logout(self, request: Request) -> Response[dict]:
        """Logout user and clear session."""
        request.clear_session()
        return Response(
            content={"message": "Logout successful"},
            status_code=HTTP_200_OK
        )

    @get("/auth/me")
    async def get_me(user: User = Provide(get_current_user)) -> UserDTO:
        return user 