from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from enum import Enum
from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import Serial
from piccolo.columns.column_types import Timestamp
from piccolo.columns.column_types import Varchar
from piccolo.columns.defaults.timestamp import TimestampNow
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table


class OrderItem(Table, tablename="order_items", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=False,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name="id",
        secret=False,
    )


ID = "2026-01-12T21:48:33:224129"
VERSION = "1.30.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="orders", description=DESCRIPTION
    )

    manager.rename_table(
        old_class_name="Order",
        old_tablename="order",
        new_class_name="Order",
        new_tablename="orders",
        schema=None,
    )

    manager.rename_table(
        old_class_name="RentalExtension",
        old_tablename="rental_extension",
        new_class_name="RentalExtension",
        new_tablename="rental_extensions",
        schema=None,
    )

    manager.rename_table(
        old_class_name="OrderItem",
        old_tablename="order_item",
        new_class_name="OrderItem",
        new_tablename="order_items",
        schema=None,
    )

    manager.rename_table(
        old_class_name="ReservationExpiry",
        old_tablename="reservation_expiry",
        new_class_name="ReservationExpiry",
        new_tablename="reservation_expiries",
        schema=None,
    )

    manager.rename_table(
        old_class_name="RentalReturn",
        old_tablename="rental_return",
        new_class_name="RentalReturn",
        new_tablename="rental_returns",
        schema=None,
    )

    manager.rename_table(
        old_class_name="Allocation",
        old_tablename="allocation",
        new_class_name="Allocation",
        new_tablename="allocations",
        schema=None,
    )

    manager.rename_table(
        old_class_name="TimeSlot",
        old_tablename="time_slot",
        new_class_name="TimeSlot",
        new_tablename="time_slots",
        schema=None,
    )

    return manager
