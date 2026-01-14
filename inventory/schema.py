from pydantic import BaseModel

class InventoryInSchema(BaseModel):
    product_id:int
    warehouse_id:int
    quantity:int