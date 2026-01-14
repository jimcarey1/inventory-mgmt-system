from litestar import Controller, post, get, Request
from litestar.response import Redirect, Template
from litestar.exceptions import HTTPException, NotFoundException, ClientException


from datetime import datetime
from .tables import Inventory
from products.tables import Product, Warehouse
from orders.tables import TimeSlot
from .schema import InventoryInSchema

def parse_ts(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return dt.replace(tzinfo=None)

class HomeController(Controller):
    path = '/'

    @get("/")
    async def home(self, department: str | None, warehouse: str | None, product: str | None, page: int = 1) -> Template:
        department = department or "Diy"
        warehouse = warehouse or "Makali Warehouse"
        product = product or ""

        limit = 10
        offset = (page - 1) * limit

        # -----------------------------
        # Paginated inventory query
        # -----------------------------
        inventories = (
            await Inventory.objects(Inventory.product, Inventory.warehouse)
            .where(Inventory.product.department == department)
            .where(Inventory.warehouse.name == warehouse)
            .where(Inventory.product.name.ilike(f"%{product}%"))
            .limit(limit)
            .offset(offset)
        )

        inventories = [inv.to_dict() for inv in inventories]

        # -----------------------------
        # Total count (for pagination UI)
        # -----------------------------
        count_sql = """
            SELECT COUNT(*) AS total
            FROM inventory i
            JOIN products p ON p.id = i.product
            JOIN warehouses w ON w.id = i.warehouse
            WHERE p.department = {}
            AND w.name = {}
            AND p.name ILIKE {}
        """
        count_rows = await Inventory.raw(count_sql, department, warehouse, f"%{product}%",)

        total_items = count_rows[0]["total"]
        total_pages = (total_items + limit - 1) // limit

        warehouses = await Warehouse.raw("SELECT id, name FROM warehouses;")
        departments = ["Robotics", "Diy", "Coding", "Astronomy", "Horticulture"]

        context_data = {
            "inventories": inventories,
            "warehouses": warehouses,
            "departments": departments,
            "department": department,
            "warehouse": warehouse,
            "product": product,
            "page": page,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages,
        }

        return Template("/core/home.html", context=context_data)



class InventoryController(Controller):
    path = "/inventory"

    @post("/add")
    async def add_product_to_warehouse(self, data:InventoryInSchema) -> Redirect:

        if data.quantity < 0:
            raise HTTPException(
                status_code=400,
                detail="Quantity cannot be negative"
            )

        try:
            product = await Product.objects().get(Product.id == data.product_id)
        except Exception as e:
            raise NotFoundException("Product not found")

        try:
            warehouse = await Warehouse.objects().get(Warehouse.id == data.warehouse_id)
        except Exception as e:
            raise NotFoundException("Warehouse not found")

        try:
            inventory = await Inventory.objects().get((Inventory.product == data.product_id)& (Inventory.warehouse == data.warehouse_id))
        except Exception as e:
            inventory = None

        if inventory:
            # Update existing stock
            await Inventory.update({Inventory.quantity: data.quantity}).where(Inventory.id == inventory.id)
            await Product.update(
                {Product.quantity: Product.quantity+data.quantity-inventory.quantity}
                ).where(Product.id == data.product_id)
        else:
            # Create new stock entry
            await Inventory.objects().create(
                product=data.product_id,
                warehouse=data.warehouse_id,
                quantity=data.quantity,
            )
            await Product.update({Product.quantity: Product.quantity + data.quantity}).where(Product.id == data.product_id)
        # Redirect back to product detail page
        return Redirect(
            path=f"/products/{data.product_id}",
            status_code=303
        )


    @get("/availability")
    async def inventory_availability(self, inventory_id: int, start_at: str, end_at: str,) -> dict:
        # 1) parse datetimes
        try:
            start_dt = parse_ts(start_at)
            end_dt = parse_ts(end_at)
        except ValueError as e:
            print(f'The error is {e}')
            raise ClientException(detail=str(e))

        if start_dt >= end_dt:
            raise ClientException(detail="start_at must be before end_at")

        # 2) fetch inventory total_quantity
        inv_rows = await Inventory.select(Inventory.quantity).where(Inventory.id == inventory_id)
        print(f'Inventory rows: {inv_rows}')
        if not inv_rows:
            raise NotFoundException("Inventory not found")

        total_qty = int(inv_rows[0]["quantity"] or 0)
        print(total_qty)
        # 3) compute booked quantity overlapping the requested window
        # overlap condition: existing.start_at < requested_end AND existing.end_at > requested_start
    
        sql = """
            SELECT COALESCE(SUM(quantity), 0) AS booked
            FROM time_slots
            WHERE inventory = {}
            AND status IN ('reserved', 'confirmed')
            AND (start_at >= {} OR end_at <= {})
            AND NOT ((start_at >= {} AND start_at >= {}) OR (end_at <= {} AND end_at <= {} ))
            """
        booked_rows = await TimeSlot.raw(sql, inventory_id, start_dt, end_dt, start_dt, end_dt, start_dt, end_dt)
        booked = int(booked_rows[0]["booked"] or 0)
        print(f'booked: {booked}')
        available = total_qty - booked

        if available < 0:
            available = 0

        return {"available": available}
