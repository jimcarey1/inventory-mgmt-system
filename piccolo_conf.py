from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine

DB = PostgresEngine(
    config={
        "database": "postgres",
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": 5432,
    }
)
APP_REGISTRY = AppRegistry(
    apps=["users.piccolo_app", "products.piccolo_app", "inventory.piccolo_app"]
)
