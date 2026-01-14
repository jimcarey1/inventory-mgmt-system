from litestar import Controller, Request, get, post, put, delete
from litestar.response import Template
from litestar.exceptions import ClientException, NotFoundException, NotAuthorizedException

from datetime import datetime, timedelta
from typing import Any

from .tables import Order, OrderItem, Allocation, TimeSlot, ReservationExpiry
from products.tables import Warehouse
from inventory.tables import Inventory

def parse_ts(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return dt.replace(tzinfo=None)

class OrderController(Controller):
    path='/orders'

    @get("/")
    async def list_orders(self, request: Request) -> Template:
        user_id = request.user.id

        sql = """
            SELECT
                id,
                status,
                created_at,
                confirmed_at,
                cancelled_at
            FROM orders
            WHERE user_id = {}
            AND status IN ('confirmed', 'completed')
            ORDER BY created_at DESC
        """
        rows = await Order.raw(sql, user_id)
        return Template(
            template_name="orders/list_orders.html",
            context={
                "orders": rows,
            },
        )


    @get("/{order_id:int}")
    async def order_detail(self, order_id: int, request: Request) -> Template:

        user = request.user
        if not user:
            raise NotAuthorizedException()

        # 1️⃣ Verify order belongs to user
        sql = """
            SELECT id, status, created_at
            FROM orders
            WHERE id = {} AND user_id = {}
            """
        order_rows = await Order.raw(sql, order_id, user.id)
        print(order_rows)

        if not order_rows:
            raise NotFoundException("Order not found")

        order = order_rows[0]

        # 2️⃣ Fetch order items
        sql = """
            SELECT
                oi.id        AS item_id,
                p.id         AS product_id,
                p.name       AS product_name,
                w.id         AS warehouse_id,
                w.name       AS warehouse_name,
                oi.quantity  AS quantity,
                oi.start_at  AS start_at,
                oi.end_at    AS end_at
            FROM order_items oi
            JOIN inventory i  ON oi.inventory = i.id
            JOIN products p   ON i.product = p.id
            JOIN warehouses w  ON i.warehouse = w.id
            WHERE oi.order_id = {}
            ORDER BY oi.start_at
            """
        items = await OrderItem.raw(sql, order_id)

        context_data = {
            "order": {
                "id": order["id"],
                "status": order["status"],
                "created_at": order["created_at"],
            },
            "items": [
                {
                    "id": row["item_id"],
                    "product": {
                        "id": row["product_id"],
                        "name": row["product_name"],
                    },
                    "warehouse": {
                        "id": row["warehouse_id"],
                        "name": row["warehouse_name"],
                    },
                    "quantity": row["quantity"],
                    "start_at": row["start_at"],
                    "end_at": row["end_at"],
                }
                for row in items
            ],
        }
        return Template('/orders/view_order.html', context=context_data)


class CartController(Controller):
    path = '/cart'

    @get("/")
    async def get_cart(self, request: Request)->Template:
        user_id = request.user.id

        sql = """
            SELECT *
            FROM orders
            WHERE user_id = {} AND status = 'draft'
            LIMIT 1
            """
        rows = await Order.raw(sql, user_id)
        if rows:
            order_id = rows[0]["id"]
        else:
            order = Order(user_id=user_id, status="draft",)
            await order.save()
            order_id = order.id

        sql = """
            SELECT 
            oi.id AS item_id, 
            oi.quantity AS item_quantity,
            oi.start_at AS item_start_at,
            oi.end_at AS item_end_at,
            p.name AS product_name,
            w.name AS warehouse_name
            FROM order_items oi
            JOIN inventory i ON oi.inventory = i.id
            JOIN products p ON i.product = p.id
            JOIN warehouses w on i.warehouse = w.id
            WHERE order_id = {}
            """
        items = await OrderItem.raw(sql, order_id)
        
        context_data = {
            "order_id":order_id,
            "items":items,
            "status":"draft",
        }
        return Template('/cart/view_cart.html', context=context_data)

    @post("/items")
    async def add_to_cart(self, request: Request)->dict[str, Any]:
        data = await request.json()
        inventory_id = int(data["inventory_id"])
        quantity = int(data["quantity"])
        start_at = parse_ts(data["start_at"])
        end_at = parse_ts(data["end_at"])
        user_id = request.user.id

        sql = "SELECT id FROM orders WHERE user_id = {} AND status = 'draft'"
        cart = await Order.raw(sql, user_id)
        if cart:
            order_id = cart[0]["id"]
        else:
            order = Order(user_id=user_id, status="draft")
            await order.save()
            order_id = order.id

        # check availability
        sql = """
            SELECT COALESCE(SUM(quantity), 0) AS booked
            FROM time_slots
            WHERE inventory = {}
            AND status IN ('reserved', 'confirmed')
            AND (start_at >= {} OR end_at <= {})
            AND NOT ((start_at >= {} AND start_at >= {}) OR (end_at <= {} AND end_at <= {} ))
            """
        availability = await TimeSlot.raw(sql, inventory_id, start_at, end_at, start_at, end_at, start_at, end_at)
        used = availability[0]["used"]

        sql = "SELECT quantity FROM inventory WHERE id = {}"
        inventory = await Inventory.raw(sql, inventory_id)

        if not inventory:
            raise NotFoundException("Inventory not found")

        if inventory[0]["quantity"] - used < quantity:
            raise ClientException("Not enough availability")

        # create order item
        item = OrderItem(
            order_id=order_id,
            inventory=inventory_id,
            quantity=quantity,
            start_at=start_at,
            end_at=end_at,
        )
        await item.save()

        # create timeslot
        slot = TimeSlot(
            inventory=inventory_id,
            quantity=quantity,
            start_at=start_at,
            end_at=end_at,
            status="reserved",
        )
        await slot.save()

        # allocation
        allocation = Allocation(
            order_item=item.id,
            time_slot=slot.id,
        )
        await allocation.save()

        # expiry
        expiry = ReservationExpiry(
            order_id=order_id,
            expires_at=datetime.now() + timedelta(minutes=15),
        )
        await expiry.save()
        return {"message": "Item added to cart", "order_item_id": item.id}

    @put("/items/{item_id:int}")
    async def update_cart_item(self, item_id: int, request: Request)->dict[str, Any]:
        data = await request.json()

        sql = """
            DELETE FROM allocations
            WHERE order_item = {}
            """
        await Allocation.raw(sql, item_id)

        sql = """
            DELETE FROM time_slots
            WHERE id IN(
                SELECT time_slot FROM allocations WHERE order_item = {}
            )
            """
        await TimeSlot.raw(sql, item_id)

        sql = """
            UPDATE order_items
            SET quantity = {},
                start_at = {},
                end_at = {}
            WHERE id = {}
            """
        
        await OrderItem.raw(sql, data['quantity'], parse_ts(data['start_at'], parse_ts(data['end_at'], item_id)))
        return {"message": "Cart item updated"}


    @delete("/items/{item_id:int}", status_code=200)
    async def remove_cart_item(self, item_id: int)->dict[str, Any]:
        sql = """
            DELETE FROM time_slots
            WHERE id IN (
                SELECT time_slot FROM allocations WHERE order_item = {}
            )
            """
        await TimeSlot.raw(sql, item_id)

        sql = "DELETE FROM allocations WHERE order_item = {}"
        await Allocation.raw(sql, item_id)

        sql =  "DELETE FROM order_items WHERE id = {}"
        await OrderItem.raw(sql, item_id)
        return {"message": "Item removed"}

    @delete("/clear", status_code=200)
    async def clear_cart(self, request: Request)->dict[str, Any]:
        user_id = request.user.id

        sql = """
            SELECT id FROM orders
            WHERE user_id = {} AND status = 'draft'
            """
        orders = await Order.raw(sql, user_id)

        if not orders:
            return {"message": "Cart empty"}
        order_id = orders[0]["id"]

        sql = """
            DELETE FROM time_slots
            WHERE id IN (
                SELECT time_slot FROM allocations
                JOIN order_items oi ON oi.id = allocations.order_item
                WHERE oi.order_id = {}
            )
            """
        await TimeSlot.raw(sql, order_id)

        sql = """
            DELETE FROM allocations
            WHERE order_item IN (
                SELECT id FROM order_items WHERE order_id = {}
            )
            """
        await Allocation.raw(sql, order_id)

        sql = "DELETE FROM order_items WHERE order_id = {}"
        await OrderItem.raw(sql, order_id)
        return {"message": "Cart cleared"}

    @post("/confirm")
    async def confirm_cart(self, request: Request)->dict[str, Any]:
        user_id = request.user.id

        sql = """
            SELECT id FROM orders
            WHERE user_id = {} AND status = 'draft'
            """
        order = await Order.raw(sql, user_id)
        if not order:
            raise ClientException("No active cart")
        order_id = order[0]["id"]

        sql = """
            UPDATE time_slots
            SET status = 'confirmed'
            WHERE id IN (
                SELECT time_slot FROM allocations
                JOIN order_items oi ON oi.id = allocations.order_item
                WHERE oi.order_id = {}
            )
            """
        await TimeSlot.raw(sql, order_id)

        sql = """
            UPDATE orders
            SET status = 'confirmed', confirmed_at=NOW()
            WHERE id={}
            """
        await Order.raw(sql, order_id)

        sql = "DELETE FROM reservation_expiries WHERE order_id = {}"
        await ReservationExpiry.raw(sql, order_id)

        return {"message": "Reservation confirmed", "order_id": order_id}
