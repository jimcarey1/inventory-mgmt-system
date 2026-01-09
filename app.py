from pathlib import Path
from typing import Optional

from litestar import Litestar
from litestar.config.csrf import CSRFConfig
from litestar.stores.file import FileStore
from litestar.connection import ASGIConnection
from litestar.middleware.session.server_side import ServerSideSessionConfig
from litestar.security.session_auth import SessionAuth

from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
from litestar.static_files import create_static_files_router

from users.controllers import UserController
from products.controllers import ProductController
from users.tables import User


csrf_config = CSRFConfig(
    secret="my-secret",
    cookie_name="csrftoken",
    header_name="x-csrftoken",
)

session_path = Path(__file__).parent / "sessions"
session_path
session_path.mkdir(parents=True, exist_ok=True)

# Use FileStore for persistent session storage
file_store = FileStore(path=session_path)

session_config = ServerSideSessionConfig(
    store="sessions"
)

async def retrieve_user_handler(
    session: dict,
    _: ASGIConnection,
) -> Optional[User]:
    user_id = session.get("user_id")
    if not user_id:
        return None
    users = await User.select().where(User.id == int(user_id))
    return users[0] if users else None


session_auth = SessionAuth(
    retrieve_user_handler=retrieve_user_handler,
    session_backend_config=session_config,
    exclude=["/static/*", "/account/login", "/account/register"],
    exclude_http_methods={
        "/account/login-user": {"POST"},
        "/account/register-user":{"POST"}
    }
)

app = Litestar(
    route_handlers=[
        UserController,
        ProductController,
        create_static_files_router(
            path="/static",
            directories=["static"],
        ),
    ],
    template_config=TemplateConfig(
        engine=JinjaTemplateEngine,
        directory=Path(__file__).parent / "templates",
    ),
    csrf_config=csrf_config,
    on_app_init=[session_auth.on_app_init],
    debug=True,
     stores={
        "sessions": file_store,   # REGISTER STORE
    },
)
