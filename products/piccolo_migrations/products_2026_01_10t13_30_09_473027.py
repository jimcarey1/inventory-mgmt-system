from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from enum import Enum
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod


ID = "2026-01-10T13:30:09:473027"
VERSION = "1.30.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="products", description=DESCRIPTION
    )

    manager.add_column(
        table_class_name="Product",
        tablename="products",
        column_name="department",
        db_column_name="department",
        column_class_name="Varchar",
        column_class=Varchar,
        params={
            "length": 255,
            "default": "Robotics",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": Enum(
                "Department",
                {
                    "robotics": "Robotics",
                    "diy": "Diy",
                    "horitculture": "Horticulture",
                    "astronomy": "Astronomy",
                    "coding": "Coding",
                },
            ),
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    return manager
