from litestar import get, post, Controller
from litestar.di import Provide
from litestar.response import Template
from litestar.exceptions import NotFoundException


from .tables import Product, Address, Warehouse
from inventory.tables import Inventory
from .schema import ProductInSchema, ProductOutSchema, WarehouseInSchema, WarehouseOutSchema, AddressSchema

from utils.permissions import admin_user_guard, handle_redirect_exception
from utils.slugify import slugify

class ProductController(Controller):
    path = '/products'

    @get('/add', guards=[admin_user_guard])
    async def add_product(self)->Template|None:
        return Template('/products/add_product.html')
    
    @post('/add-product', guards=[admin_user_guard])
    async def post_add_product(self, data:ProductInSchema)->ProductOutSchema:
        slug = slugify(data.name)
        if data.description:
            product = Product(name=data.name, description=data.description, price=data.price, slug=slug)
        else:
            product = Product(name=data.name, price=data.price, slug=data.slug)

        await product.save()
        return product
    
    @get("/{product_id:int}", guards=[admin_user_guard])
    async def get_product_with_warehouses(self, product_id: int) -> Template:
        product = (
            await Product.objects()
            .where(Product.id == product_id)
            .first()
        )

        if not product:
            raise NotFoundException("Product not found")
        
        sql ="""
                SELECT
                warehouses.id AS warehouse_id,
                warehouses.name AS warehouse_name,
                addresses.city  AS address_city,
                addresses.state AS address_state,
                inventory.quantity AS quantity
                FROM inventory
                JOIN warehouses ON inventory.warehouse = warehouses.id
                LEFT JOIN addresses ON warehouses.address = addresses.id
                WHERE inventory.product = {}
            """
        rows = await Inventory.raw(sql, product_id)
        warehouses = [
            {
                "id": row["warehouse_id"],
                "name": row["warehouse_name"],
                "city": row["address_city"],
                "state": row["address_state"],
                "quantity":row["quantity"]
            }
            for row in rows
        ]
        all_warehouses = await Warehouse.select(Warehouse.id, Warehouse.name)
        context_data = {
            "product":product.to_dict(),
            "product_warehouses": warehouses,
            "warehouses": all_warehouses
        }
        return Template('/products/view_product.html', context=context_data)
    

class WarehouseController(Controller):
    path = '/warehouse'

    @get('/add', guards=[admin_user_guard])
    async def add(self)->Template:
        return Template('/products/add_warehouse.html')
    
    @post('/add-warehouse', guards=[admin_user_guard])
    async def add_warehouse(self, data:WarehouseInSchema)->WarehouseOutSchema:
        address = await Address.objects().get(Address.id == data.address_id)
        warehouse = Warehouse(
            name=data.name,
            address=address
        )
        await warehouse.save()
        return warehouse.to_dict()
    
    @get('/{warehouse_id:int}', guards=[admin_user_guard])
    async def get_warehouse(self, warehouse_id:int)->Template:
        sql = """
            SELECT
            w.id as wid,
            w.name as wname,
            w.updated_on as wupdated_on,
            a.line1 as wline1,
            a.line2 as wline2,
            a.city as wcity,
            a.state as wstate,
            a.country as wcountry,
            a.postal_code as wpostal_code,
            a.latitude as wlatitude,
            a.longitute as wlongitute
            FROM warehouses w
            JOIN addresses a ON w.id = a.id
            WHERE w.id = {}
            """
        warehouse = await Warehouse.raw(sql, warehouse_id)
        if len(warehouse)>0:
            warehouse = warehouse[0]

        sql = """
            SELECT
            products.id AS id,
            products.name AS name,
            products.price AS price,
            products.department AS department,
            inventory.quantity AS quantity
            FROM inventory
            JOIN products ON inventory.product = products.id
            WHERE inventory.warehouse = {}
            """
        products = await Inventory.raw(sql, warehouse_id)
        context_data = {
            "warehouse":warehouse,
            "inventory":products
        }
        return Template('/products/view_warehouse.html', context=context_data)


class AddressController(Controller):
    path = '/addresses'
    
    @post('/add', guards=[admin_user_guard])
    async def add(self, data:AddressSchema)->AddressSchema:
        address = Address(
            line1 = data.line1, 
            line2=data.line2,
            city=data.city,
            state=data.state,
            postal_code=data.postal_code,
            country=data.country,
            latitude=data.latitude,
            longitute=data.longitude,
            )
        await address.save()
        return address.to_dict()
