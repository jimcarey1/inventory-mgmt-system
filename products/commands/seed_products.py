from faker import Faker
import random
from products.tables import Product
import re
import unicodedata

def slugify(value):
    """
    Converts to lowercase, removes non-word characters, and converts spaces to hyphens.
    Handles basic ASCII transliteration.
    """
    # Normalize unicode characters and encode/decode to convert to ASCII representation
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    # Remove non-alphanumeric, whitespace, or hyphen characters
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    # Replace whitespace/hyphen sequences with a single hyphen
    value = re.sub(r'[-\s]+', '-', value)
    return value


fake = Faker()

DEPARTMENTS = [
    "Robotics",
    "Diy",
    "Horticulture",
    "Astronomy",
    "Coding"
]

async def generate_product():
    products = []
    for i in range(100):
        name = fake.unique.word().capitalize() + " " + fake.word().capitalize()

        product = Product(name=name, slug=slugify(name), department= fake.random_element(DEPARTMENTS), description= fake.sentence(nb_words=12), price= round(random.uniform(500, 10000), 2))
        products.append(product)
    await Product.insert(*products)
