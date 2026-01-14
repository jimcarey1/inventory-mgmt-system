# app.py (Litestar)
from litestar import Litestar, post
from piccolo.table import Table
from piccolo.columns import Integer, UUID
from piccolo.engine.postgres import PostgresEngine

DB = PostgresEngine(conn_uri="postgresql://...")

class StockLevel(Table):
    product_id = UUID()
    warehouse_id = UUID()
    qty_on_hand = Integer()
    qty_reserved = Integer()

    class Meta:
        db = DB

@post("/orders/{order_id}/reserve")
async def reserve_stock(order_id: str, body: dict) -> dict:
    product_id = body["product_id"]
    warehouse_id = body["warehouse_id"]
    qty = int(body["qty"])

    # Start transaction
    async with DB.transaction():
        # Lock the row(s) to prevent races
        rows = await StockLevel.select(
            (StockLevel.product_id == product_id) &
            (StockLevel.warehouse_id == warehouse_id)
        ).lock_rows().run()
        if not rows:
            raise Exception("No stock record")

        row = rows[0]
        available = row.qty_on_hand - row.qty_reserved
        if available < qty:
            return {"status": "failed", "reason": "insufficient_stock"}

        # update_reserved: use an atomic update
        await StockLevel.update(
            {StockLevel.qty_reserved: StockLevel.qty_reserved + qty}
        ).where(
            (StockLevel.product_id == product_id) &
            (StockLevel.warehouse_id == warehouse_id)
        ).run()

        # write inventory transaction (audit)
        # await InventoryTransaction.insert(...).run()

    return {"status": "ok", "reserved": qty}
