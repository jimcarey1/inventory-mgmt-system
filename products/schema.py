from pydantic import BaseModel, UUID4

class ProductOutSchema(BaseModel):
    id:int
    name:str
    sku:UUID4

class ProductInSchema(BaseModel):
    name:str
    description:str|None = None


class AddressSchema(BaseModel):
    id: int|None = None
    line1: str
    line2: str|None = None
    city: str
    state: str
    postal_code: str
    country: str
    is_primary: bool = True
    longitute: float|None = None
    latittude: float|None = None

class WarehouseInSchema(BaseModel):
    name: str

class WarehouseOutSchema(BaseModel):
    id: int
    name: str
    address: AddressSchema