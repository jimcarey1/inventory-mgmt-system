from litestar.exceptions import PermissionDeniedException, NotAuthorizedException
from litestar.connection import ASGIConnection
from litestar.handlers import BaseRouteHandler
from litestar import Request
from litestar.response import Redirect

async def admin_user_guard(connection:ASGIConnection, handler:BaseRouteHandler) -> None:
    if not connection.user.is_admin:
        raise PermissionDeniedException("Admin access required")

async def require_authenticated(connection:ASGIConnection, handler:BaseRouteHandler) -> None:
    if connection.user is None:
        raise NotAuthorizedException("authentication required")
    
def handle_redirect_exception(request: Request, exc: Exception) -> Redirect:
    return Redirect(path="/")

def go_to_login_page(request: Request, exc: Exception) -> Redirect:
    return Redirect(path='/account/login')
