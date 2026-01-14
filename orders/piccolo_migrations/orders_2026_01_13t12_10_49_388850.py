from piccolo.apps.migrations.auto.migration_manager import MigrationManager


ID = "2026-01-13T12:10:49:388850"
VERSION = "1.30.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="orders", description=DESCRIPTION
    )

    manager.rename_column(
        table_class_name="OrderItem",
        tablename="order_items",
        old_column_name="order",
        new_column_name="order_id",
        old_db_column_name="order",
        new_db_column_name="order_id",
        schema=None,
    )

    manager.rename_column(
        table_class_name="ReservationExpiry",
        tablename="reservation_expiries",
        old_column_name="order",
        new_column_name="order_id",
        old_db_column_name="order",
        new_db_column_name="order_id",
        schema=None,
    )

    return manager
