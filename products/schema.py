from pydantic import BaseModel, UUID4

class ProductOutSchema(BaseModel):
    id:int
    name:str
    sku:UUID4
    slug:str
    price:float

class ProductInSchema(BaseModel):
    name:str
    description:str|None = None
    price:float = 0


class AddressSchema(BaseModel):
    id: int|None = None
    line1: str
    line2: str|None = None
    city: str
    state: str
    postal_code: str
    country: str
    is_primary: bool = True
    longitude: float|None = None
    latitude: float|None = None

class WarehouseInSchema(BaseModel):
    name: str
    address_id:int = 0

class WarehouseOutSchema(BaseModel):
    id: int
    name: str
    address: AddressSchema