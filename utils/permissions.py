from litestar.exceptions import NotAuthorizedException

async def require_authenticated(connection, handler) -> None:
    if connection.user is None:
        raise NotAuthorizedException("authentication required")
