import json


class Product:
    def __init__(self, name, category, price_per_kg):
        self.name = name
        self.category = category
        self.price_per_kg = price_per_kg

    def __str__(self):
        return f"{self.name} - ₹{self.price_per_kg}/kg"


def load_products():
    with open("data/products.json", "r") as file:
        data = json.load(file)

    products = []

    for item in data:
        product = Product(
        item["name"],
        item["category"],
        item["price_per_kg"]
    )

        products.append(product)

    return products

def load_shops():

    with open("data/shops.json", "r") as file:
        return json.load(file)

def get_shop_by_subdomain(subdomain):

    shops = load_shops()

    for shop in shops:

        if shop["subdomain"].lower() == subdomain.lower():
            return shop

    return None
