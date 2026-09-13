from flask import Flask, render_template, request, session, redirect, url_for, flash
from products import load_products, load_shops, get_shop_by_subdomain
from orders import (
    Order,
    save_order,
    load_orders,
    get_today_sales,
    get_today_order_count,
    get_today_items_sold,
    get_today_average_order_value,
    get_today_product_sales,
    get_today_orders,
    get_current_orders,
    update_order_status,
    ALLOWED_STATUS_TRANSITIONS,
    get_all_orders
)

from customer import Customer


app = Flask(__name__)
app.secret_key = "buddy-secret-key"

VERIFY_TOKEN = "buddy-webhook-token"

def build_cart_items():

    cart = session.get("cart", [])
    products = load_products()

    cart_items = []

    for item in cart:

        for product in products:

            if product.name == item["product"]:

                quantity = item["quantity"]

                price = product.price_per_kg * (quantity / 1000)

                cart_items.append({
                    "product": product.name,
                    "quantity": quantity,
                    "price": price,
                    "shop_subdomain": item.get("shop_subdomain")
                })

                break

    return cart_items


def calculate_cart_total(cart_items):

    total = 0

    for item in cart_items:
        total += item["price"]

    return total


def format_quantity(grams):

    if grams < 1000:
        return f"{grams} g"

    kg = grams / 1000

    if kg.is_integer():
        return f"{int(kg)} kg"

    return f"{kg:g} kg"


@app.route("/")
def home():

    products = load_products()

    return render_template(
        "home.html",
        products=products
    )


@app.route("/menu")
def menu():

    products = load_products()

    category = request.args.get("category")

    if category:
        products = [
            product
            for product in products
            if product.category.lower() == category.lower()
        ]

    return render_template(
        "menu.html",
        products=products,
        category=category
    )


@app.route("/shop/<subdomain>/menu")
def shop_menu(subdomain):

    shop = get_shop_by_subdomain(subdomain)

    if shop is None:
        return "Shop not found", 404

    session["shop_subdomain"] = shop["subdomain"]

    products = load_products()

    category = request.args.get("category")

    if category:
        products = [
            product
            for product in products
            if product.category.lower() == category.lower()
        ]

    return render_template(
        "menu.html",
        products=products,
        category=category,
        shop=shop
    )


@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():

    product_name = request.form["product"]
    quantity = int(request.form["quantity"])
    shop_subdomain = request.form.get("shop_subdomain")

    if "cart" not in session:
        session["cart"] = []

    for item in session["cart"]:

        if item["product"] == product_name:

            item["quantity"] += quantity
            session.modified = True

            flash(
                f"{quantity} g more of {product_name} added to cart."
            )

            if shop_subdomain:
                return redirect(
                    url_for("shop_menu", subdomain=shop_subdomain)
                )

            return redirect(url_for("menu"))

    session["cart"].append({
        "product": product_name,
        "quantity": quantity,
        "shop_subdomain": shop_subdomain
    })

    session.modified = True

    flash(
        f"{product_name} ({quantity} g) added to cart."
    )

    if shop_subdomain:
        return redirect(
            url_for("shop_menu", subdomain=shop_subdomain)
        )

    return redirect(url_for("menu"))


@app.route("/update-cart", methods=["POST"])
def update_cart():

    product_name = request.form["product"]
    quantity = int(request.form["quantity"])

    for item in session["cart"]:

        if item["product"] == product_name:
            item["quantity"] = quantity
            session.modified = True
            break

    shop_subdomain = None

    if session["cart"]:
        shop_subdomain = session["cart"][0].get("shop_subdomain")

    if shop_subdomain:
        return redirect(
            url_for("cart", shop=shop_subdomain)
        )

    return redirect(url_for("cart"))


@app.route("/remove-from-cart", methods=["POST"])
def remove_from_cart():

    product_name = request.form["product"]

    for item in session["cart"]:

        if item["product"] == product_name:
            session["cart"].remove(item)
            session.modified = True
            break

    return redirect(url_for("cart"))


@app.route("/cart")
def cart():

    cart_items = build_cart_items()
    total = calculate_cart_total(cart_items)

    shop = None

    shop_subdomain = session.get("shop_subdomain")

    if shop_subdomain:
        shop = get_shop_by_subdomain(shop_subdomain)

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total,
        shop=shop
    )


@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    cart_items = build_cart_items()

    if not cart_items:
        return "Your cart is empty."

    total = calculate_cart_total(cart_items)

    shop = None

    shop_subdomain = cart_items[0].get("shop_subdomain")

    if shop_subdomain:
        shop = get_shop_by_subdomain(shop_subdomain)

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total=total,
        shop=shop
    )


@app.route("/place-order", methods=["POST"])
def place_order():

    name = request.form["name"].strip()
    phone = request.form["phone"].strip()

    errors = []

    if not name or not name.replace(" ", "").isalpha():
        errors.append("Invalid name.")

    if not phone.isdigit() or len(phone) != 10:
        errors.append("Invalid phone number.")

    if errors:
        return " ".join(errors)

    customer = Customer(name, phone)

    shop_subdomain = session.get("shop_subdomain")

    if not shop_subdomain:
        return "Shop not selected.", 400

    order = Order(customer, shop_subdomain)

    products = load_products()
    cart = session.get("cart", [])

    for item in cart:

        for product in products:

            if product.name == item["product"]:

                order.add_item(
                    product,
                    item["quantity"]
                )

                break

    save_order(order)

    session.pop("cart", None)

    return render_template(
    "order_success.html",
    order=order
)


@app.route("/dashboard")
def dashboard():

    status_filter = request.args.get("status")

    order_count = get_today_order_count()
    total_sales = get_today_sales()
    chicken_grams, mutton_grams = get_today_items_sold()
    average_order_value = get_today_average_order_value()
    product_sales = get_today_product_sales()

    sorted_product_sales = sorted(
        product_sales.items(),
        key=lambda item: item[1],
        reverse=True
    )

    today_orders = get_today_orders()

    if status_filter:
        today_orders = [
            order
            for order in today_orders
            if order.get("status", "New") == status_filter
        ]

    return render_template(
        "dashboard.html",
        order_count=order_count,
        total_sales=total_sales,
        chicken_quantity=format_quantity(chicken_grams),
        mutton_quantity=format_quantity(mutton_grams),
        average_order_value=average_order_value,
        product_sales=sorted_product_sales,
        today_orders=today_orders,
        status_filter=status_filter,
        allowed_transitions=ALLOWED_STATUS_TRANSITIONS
    )


@app.route("/order/<int:order_id>")
def order_details(order_id):

    orders = load_orders()

    for order in orders:

        if order["order_id"] == order_id:

            return render_template(
                "order_details.html",
                order=order
            )

    return "Order not found."


@app.route("/search-order")
def search_order():

    return render_template("order_search.html")


@app.route("/search-order", methods=["POST"])
def search_order_submit():

    order_id = int(request.form["order_id"])

    orders = load_orders()

    for order in orders:

        if order["order_id"] == order_id:

            return render_template(
                "order_details.html",
                order=order
            )

    return "Order not found."


@app.route("/search-customer", methods=["POST"])
def search_customer():

    name = request.form["name"].strip()

    orders = load_orders()

    matching_orders = []

    for order in orders:

        customer_name = order["customer"]["name"]

        if customer_name.lower() == name.lower():
            matching_orders.append(order)

    return render_template(
        "customer_orders.html",
        name=name,
        orders=matching_orders
    )


@app.route("/update-status", methods=["POST"])
def update_status():

    order_id = int(request.form["order_id"])
    new_status = request.form["status"]

    success = update_order_status(order_id, new_status)

    if not success:
        flash("Invalid status change.")

    return redirect(request.referrer)


@app.route("/orders")
def orders_page():

    status_filter = request.args.get("status")
    date_filter = request.args.get("date")

    all_orders = get_all_orders()

    if status_filter:
        all_orders = [
            order
            for order in all_orders
            if order.get("status", "New") == status_filter
        ]

    if date_filter:
        all_orders = [
            order
            for order in all_orders
            if order.get("created_at", "")[:10] == date_filter
        ]

    return render_template(
        "orders.html",
        orders=all_orders,
        status_filter=status_filter,
        date_filter=date_filter
    )


@app.route("/current-orders")
def current_orders_page():

    current_orders = get_current_orders()

    return render_template(
        "current_orders.html",
        orders=current_orders,
        allowed_transitions=ALLOWED_STATUS_TRANSITIONS
    )


@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    if request.method == "GET":

        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("Webhook verified!")
            return challenge, 200

        print("Webhook verification failed.")
        return "Forbidden", 403

    data = request.get_json()

    print("Webhook received!")
    print("Full data:", data)

    try:

        message_data = data["entry"][0]["changes"][0]["value"]["messages"][0]

        sender = message_data["from"]

        message = message_data["text"]["body"]

        print("Sender:", sender)
        print("Message:", message)

    except (KeyError, IndexError, TypeError):

        print("Could not understand webhook data.")
        return "Invalid webhook data", 400

    return "OK", 200


@app.route("/shop/<subdomain>")
def shop(subdomain):

    shop = get_shop_by_subdomain(subdomain)

    if shop is None:
        return "Shop not found", 404

    session["shop_subdomain"] = shop["subdomain"]

    products = load_products()

    return render_template(
        "home.html",
        products=products,
        shop=shop
    )


if __name__ == "__main__":

    shops = load_shops()

    print("Available shops:")

    for shop in shops:
        print(
            shop["shop_id"],
            "|",
            shop["shop_name"],
            "|",
            shop["subdomain"]
        )

    app.run(debug=True)
