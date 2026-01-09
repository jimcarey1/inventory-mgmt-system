from piccolo.table import Table
from piccolo.columns import Varchar, Text, Timestamp, Integer, UUID, Boolean, Float, ForeignKey


from datetime import datetime

class Product(Table, tablename='products'):
    name = Varchar(unique=True)
    slug = Varchar()
    sku = UUID()
    description = Text(null=True)
    quantity = Integer(default=0)
    price = Float(default=0)
    created_on = Timestamp()
    updated_on = Timestamp(auto_update=datetime.now)

class Address(Table, tablename='addresses'):
    line1 = Text()
    line2 = Text(null=True)
    city = Varchar(length=100)
    state = Varchar(length=100)
    postal_code = Varchar(length=20)
    country = Varchar(length=100, default='India')
    is_primary = Boolean(default=True)

    latitude = Float(null=True)
    longitute = Float(null=True)


class Warehouse(Table, tablename='warehouses'):
    name = Varchar(unique=True)
    address = ForeignKey(Address, unique=True, null=True)
    created_on = Timestamp()
    updated_on = Timestamp(auto_update=datetime.now)