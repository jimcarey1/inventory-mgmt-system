from litestar import get, post, Controller
from litestar.di import Provide
from litestar.response import Template

from .tables import Product, Address, Warehouse
from .schema import *

from utils.permissions import require_authenticated

class ProductController(Controller):
    path = '/products'
    guards = [require_authenticated]

    @get('/add')
    async def add_product(self)->Template:
        try:
            return Template('/products/add_product.html')
        except Exception as e:
            print(e)
