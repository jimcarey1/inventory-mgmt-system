from piccolo.table import Table
from piccolo.columns import ForeignKey, Integer

from products.tables import Product, Warehouse

class Inventory(Table, tablename='inventory'):
    product = ForeignKey(Product)
    warehouse = ForeignKey(Warehouse)
    quantity = Integer()

    class Meta:
        unique_together = (('product', 'warehouse'))