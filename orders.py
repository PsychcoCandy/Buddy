import json
from datetime import datetime


ALLOWED_STATUS_TRANSITIONS = {
    "New": ["Confirmed", "Cancelled"],
    "Confirmed": ["Preparing"],
    "Preparing": ["Ready"],
    "Ready": ["Out for Delivery"],
    "Out for Delivery": ["Delivered"],
    "Delivered": [],
    "Cancelled": []
}


class OrderItem:
    def __init__(self, product, quantity_grams):
        self.product = product
        self.quantity_grams = quantity_grams

    def calculate_price(self):
        return self.product.price_per_kg * (self.quantity_grams / 1000)


def get_next_order_id():
    try:
        with open("data/orders.json", "r") as file:
            orders = json.load(file)

        if not orders:
            return 1001

        highest_id = max(order["order_id"] for order in orders)

        return highest_id + 1

    except (FileNotFoundError, json.JSONDecodeError):
        return 1001


class Order:

    def __init__(self, customer, shop_subdomain):
        self.order_id = get_next_order_id()
        self.customer = customer
        self.shop_subdomain = shop_subdomain
        self.items = []
        self.created_at = datetime.now()
        self.status = "New"

    def add_item(self, product, quantity_grams):

        for existing_item in self.items:

            if existing_item.product.name == product.name:
                existing_item.quantity_grams += quantity_grams
                return

        item = OrderItem(product, quantity_grams)
        self.items.append(item)
            
    def update_quantity(self, index, quantity):
        self.items[index].quantity_grams = quantity

    def calculate_total(self):
        total = 0

        for item in self.items:
            total += item.calculate_price()

        return total

    def print_current_order(self):
        print("\n----- CURRENT ORDER -----\n")

        if not self.items:
            print("No items added yet.")
            return

        for item in self.items:
            print(
                f"{item.product.name} | "
                f"{item.quantity_grams} g | "
                f"₹{item.calculate_price():.2f}"
            )

        print("-------------------------")
        print(f"CURRENT TOTAL: ₹{self.calculate_total():.2f}")

    def print_receipt(self):
        print("\n----- ORDER RECEIPT -----\n")

        print(f"Order ID: {self.order_id}")
        print(f"Customer: {self.customer.name}")
        print(f"Phone: {self.customer.phone}")
        

        for item in self.items:
            print(
                f"{item.product.name} | "
                f"{item.quantity_grams} g | "
                f"₹{item.product.price_per_kg}/kg | "
                f"₹{item.calculate_price():.2f}"
            )

        print("-------------------------")
        print(f"TOTAL: ₹{self.calculate_total():.2f}")


    def to_dict(self):
        return {
            "order_id": self.order_id,
            "shop_subdomain": self.shop_subdomain,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "customer": {
                "name": self.customer.name,
                "phone": self.customer.phone
            },
            "items": [
                {
                    "product": item.product.name,
                    "quantity_grams": item.quantity_grams,
                    "price": item.calculate_price()
                }
                for item in self.items
            ],
            "total": self.calculate_total()
        }


    def remove_item(self, index):
        self.items.pop(index)


def save_order(order):

    try:
        with open("data/orders.json", "r") as file:
            orders = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        orders = []

    orders.append(order.to_dict())

    with open("data/orders.json", "w") as file:
        json.dump(orders, file, indent=4)

    backup_orders()


def load_orders():

    try:
        with open("data/orders.json", "r") as file:
            return json.load(file)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        print("Warning: Orders data could not be read.")
        return []


def backup_orders():

    try:
        with open("data/orders.json", "r") as file:
            orders = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return

    with open("data/orders_backup.json", "w") as file:
        json.dump(orders, file, indent=4)


def view_orders():
    orders = load_orders()

    if not orders:
        print("\nNo orders found.")
        return

    print("\n===== ORDER HISTORY =====")

    for order in orders:
        print(f"\nOrder ID: {order['order_id']}")
        print(f"Customer: {order['customer']['name']}")
        print(f"Phone: {order['customer']['phone']}")

        for item in order["items"]:
            print(
                f"  {item['product']} | "
                f"{item['quantity_grams']} g | "
                f"₹{item['price']:.2f}"
            )

        print(f"Total: ₹{order['total']:.2f}")
        print("-------------------------")


def view_today_orders():

    orders = load_orders()
    today = datetime.now().date()

    found = False

    for order in orders:

        if "created_at" not in order:
            continue

        order_date = datetime.fromisoformat(
            order["created_at"]
        ).date()

        if order_date == today:
            print_saved_order(order)
            found = True

    if not found:
        print("\nNo orders found for today.")


def get_today_sales():

    orders = load_orders()
    today = datetime.now().date()

    total_sales = 0

    for order in orders:

        if order.get("status", "New") not in [
            "Confirmed",
            "Preparing",
            "Ready",
            "Out for Delivery",
            "Delivered"
        ]:
            continue

        if "created_at" not in order:
            continue

        order_date = datetime.fromisoformat(
            order["created_at"]
        ).date()

        if order_date == today:
            total_sales += order["total"]

    return total_sales


def view_today_product_sales():

    product_sales = get_today_product_sales()

    if not product_sales:
        print("\nNo sales today.")
        return

    sorted_products = sorted(
        product_sales.items(),
        key=lambda item: item[1],
        reverse=True
    )

    print("\n===== TODAY'S BEST SELLERS =====\n")

    for number, (product, quantity) in enumerate(sorted_products, start=1):
        print(f"{number}. {product} | {quantity} g")
    print("==============================")

def get_today_order_count():

    orders = load_orders()
    today = datetime.now().date()

    count = 0

    for order in orders:

        if "created_at" not in order:
            continue

        order_date = datetime.fromisoformat(
            order["created_at"]
        ).date()

        if order_date == today:
            count += 1

    return count


def get_today_items_sold():

    orders = load_orders()
    today = datetime.now().date()

    chicken_grams = 0
    mutton_grams = 0

    for order in orders:

        if order.get("status", "New") not in [
            "Confirmed",
            "Preparing",
            "Ready",
            "Out for Delivery",
            "Delivered"
        ]:
            continue

        if "created_at" not in order:
            continue

        order_date = datetime.fromisoformat(
            order["created_at"]
        ).date()

        if order_date == today:

            for item in order["items"]:

                product_name = item["product"].lower()

                if "chicken" in product_name:
                    chicken_grams += item["quantity_grams"]

                elif "mutton" in product_name:
                    mutton_grams += item["quantity_grams"]

    return chicken_grams, mutton_grams


def get_today_average_order_value():

    order_count = get_today_order_count()

    if order_count == 0:
        return 0

    total_sales = get_today_sales()

    return total_sales / order_count


def view_today_summary():

    order_count = get_today_order_count()
    total_sales = get_today_sales()
    total_grams = get_today_items_sold()
    average_order_value = get_today_average_order_value()

    print("\n================================")
    print("          TODAY'S SUMMARY")
    print("================================\n")

    print(f"Orders:               {order_count}")
    print(f"Total quantity:       {total_grams} g")
    print(f"Total sales:          ₹{total_sales:.2f}")
    print(f"Average order value:  ₹{average_order_value:.2f}")
    print("================================")

    print("\n================================")
    print("          BEST SELLERS")
    print("================================\n")

    product_sales = get_today_product_sales()

    if not product_sales:
        print("No sales today.")

    else:
        sorted_products = sorted(
            product_sales.items(),
            key=lambda item: item[1],
            reverse=True
        )

        for number, (product, quantity) in enumerate(
            sorted_products,
            start=1
        ):
            print(f"{number}. {product} | {quantity} g")

    print("================================")


def get_today_product_sales():

    orders = load_orders()
    today = datetime.now().date()

    product_sales = {}

    for order in orders:

        if "created_at" not in order:
            continue

        order_date = datetime.fromisoformat(
            order["created_at"]
        ).date()

        if order_date == today:

            for item in order["items"]:

                product = item["product"]
                quantity = item["quantity_grams"]

                if product not in product_sales:
                    product_sales[product] = 0

                product_sales[product] += quantity

    return product_sales


def print_saved_order(order):

    print("\n----- ORDER DETAILS -----\n")

    print(f"Order ID: {order['order_id']}")
    print(f"Customer: {order['customer']['name']}")
    print(f"Phone: {order['customer']['phone']}")

    for item in order["items"]:
        print(
            f"{item['product']} | "
            f"{item['quantity_grams']} g | "
            f"₹{item['price']:.2f}"
        )

    print("-------------------------")
    print(f"TOTAL: ₹{order['total']:.2f}")


def get_today_orders():

    orders = load_orders()
    today = datetime.now().date()

    today_orders = []

    for order in orders:

        if "created_at" not in order:
            continue

        order_date = datetime.fromisoformat(
            order["created_at"]
        ).date()

        if order_date == today:
            today_orders.append(order)

    return today_orders


def get_all_orders():

    orders = load_orders()

    orders.sort(
        key=lambda order: order.get("created_at", ""),
        reverse=True
    )

    return orders


def get_current_orders():

    orders = load_orders()

    current_statuses = [
        "New",
        "Confirmed",
        "Preparing",
        "Ready",
        "Out for Delivery"
    ]

    current_orders = [
        order
        for order in orders
        if order.get("status", "New") in current_statuses
    ]

    current_orders.sort(
        key=lambda order: order["order_id"]
    )

    return current_orders


def update_order_status(order_id, new_status):

    orders = load_orders()

    for order in orders:

        if order["order_id"] == order_id:

            current_status = order.get("status", "New")

            if new_status not in ALLOWED_STATUS_TRANSITIONS[current_status]:
                return False

            order["status"] = new_status

            with open("data/orders.json", "w") as file:
                json.dump(orders, file, indent=4)

            backup_orders()

            return True

    return False

