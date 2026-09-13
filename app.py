from products import load_products
from orders import Order, save_order, view_orders, load_orders, print_saved_order, view_today_orders, view_today_summary
from customer import Customer


# =========================
# INPUT HELPERS
# =========================

def get_name():

    while True:
        name = input("\nCustomer name: ")

        if name.replace(" ", "").isalpha():
            return name

        print("\nInvalid name. Please enter letters only.")


def get_phone():

    while True:
        phone = input("Phone number: ")

        if not phone.isdigit():
            print("\nInvalid phone number. Please enter digits only.")
            continue

        if len(phone) != 10:
            print("\nInvalid phone number. Please enter a 10-digit number.")
            continue

        return phone


def get_customer():

    name = get_name()
    phone = get_phone()

    return Customer(name, phone)


def get_quantity():

    while True:
        try:
            quantity = int(input("How many grams? "))

            if quantity <= 0:
                print("\nQuantity must be greater than 0.")
                continue

            return quantity

        except ValueError:
            print("\nPlease enter a valid number.")


def get_product_choice(products):

    while True:
        try:
            choice = int(input("Choose a product: "))

            if choice == 7 or choice == 8 or choice == 9 or choice == 0:
                return choice

            if choice < 1 or choice > len(products):
                print("\nInvalid choice. Please try again.")
                continue

            return choice

        except ValueError:
            print("\nPlease enter a number.")


def get_confirmation(message):

    while True:
        confirm = input(f"{message} (y/n): ").strip().lower()

        if confirm == "y":
            return True

        if confirm == "n":
            return False

        print("\nPlease enter y or n.")


def get_order_menu_choice(products):

    while True:
        try:
            choice = int(input("Choose a product or option: "))

            if choice == 0:
                return choice

            if choice == 7:
                return choice

            if choice == 8:
                return choice

            if choice == 9:
                return choice

            if 1 <= choice <= len(products):
                return choice

            print("\nInvalid choice. Please try again.")

        except ValueError:
            print("\nPlease enter a number.")


# =========================
# ORDER FUNCTIONS
# =========================

def take_order(order, products):

    while True:

        print("\n----- NEW ORDER -----\n")
        for number, product in enumerate(products, start=1):
            print(f"{number}. {product}")
        
        print("\n----------------------------------")
        print("\n7. Edit quantity")
        print("8. Remove item")
        print("9. Finish order")
        print("0. Cancel order\n")
        

        choice = get_order_menu_choice(products)

        if choice == 7:
            edit_item(order)
            continue
    
        if choice == 8:
            remove_item(order)
            order.print_current_order()
            continue

        if choice == 9:

            if not order.items:
                print("\nYou haven't added any items yet.")
                continue

            if get_confirmation("Finish order?"):
                break

            continue

        if choice == 0:
        
            if get_confirmation("Cancel this order?"):
                print("Order cancelled.")
                return None

            continue

        selected_product = products[choice - 1]

        print("\nYou selected:", selected_product)

        quantity = get_quantity()

        order.add_item(selected_product, quantity)
        order.print_current_order()

    return order


def remove_item(order):

    if not order.items:
        print("\nThere are no items to remove.")
        return
    
    show_order_items(order)

    print("0. Cancel")

    try:
        choice = int(input("Choose an item to remove: "))
    except ValueError:
        print("\nPlease enter a number.")
        return

    if choice == 0:
        return

    if choice < 1 or choice > len(order.items):
        print("Invalid choice.")
        return

    if get_confirmation("Remove this item?"):
        order.remove_item(choice - 1)
        print("\nItem removed successfully.")
    else:
        print("\nItem was not removed.")


def edit_item(order):

    if not order.items:
        print("\nThere are no items to edit.")
        return

    show_order_items(order)

    print("0. Cancel")

    while True:
        try:
            choice = int(input("Choose an item to edit: "))

            if choice == 0:
                return

            if choice < 1 or choice > len(order.items):
                print("\nInvalid choice. Please try again.")
                continue

            break

        except ValueError:
            print("\nPlease enter a number.")

    while True:
        try:
            quantity = int(input("Enter new quantity in grams: "))

            if quantity <= 0:
                print("\nQuantity must be greater than 0.")
                continue

            break

        except ValueError:
            print("\nPlease enter a valid number.")

    item = order.items[choice - 1]

    print(
        f"Change {item.product.name} "
        f"from {item.quantity_grams} g to {quantity} g?"
    )

    if get_confirmation("Confirm change?"):
        order.update_quantity(choice - 1, quantity)

        print("\nQuantity updated successfully.")
        order.print_current_order()
    else:
        print("\nQuantity was not changed.")


def show_order_items(order):

    if not order.items:
        print("\nThere are no items in this order.")
        return False

    print("\n----- CURRENT ITEMS -----\n")

    for number, item in enumerate(order.items, start=1):
        print(
            f"{number}. "
            f"{item.product.name} | "
            f"{item.quantity_grams} g | "
            f"₹{item.calculate_price():.2f}"
        )

    return True


# =========================
# SEARCH FUNCTIONS
# =========================

def search_orders():

    while True:
        print("\n===== SEARCH ORDERS =====\n")
        print("1. Search by Order ID")
        print("2. Search by Customer Name")
        print("0. Back\n")

        try:
            choice = int(input("Choose an option: "))
        except ValueError:
            print("\nPlease enter a number.")
            continue

        if choice == 1:
            try:
                order_id = int(input("Enter Order ID: "))
            except ValueError:
                print("\nPlease enter a valid Order ID.")
                continue

            find_order_by_id(order_id)

        elif choice == 2:
            name = input("Enter customer name: ").strip()

            if not name:
                print("\nPlease enter a name.")
                continue

            find_orders_by_customer(name)

        elif choice == 0:
            break

        else:
            print("\nInvalid choice. Please try again.")


def find_order_by_id(order_id):

    orders = load_orders()

    for order in orders:
        if order["order_id"] == order_id:
            print_saved_order(order)
            return

    print("\nOrder not found.")


def find_orders_by_customer(name):

    orders = load_orders()
    found = False

    for order in orders:
        if order["customer"]["name"].lower() == name.lower():
            print_saved_order(order)
            found = True

    if not found:
        print("\nNo orders found for this customer.")


# =========================
# MENU
# =========================

def main_menu(products):

    while True:
        print("\n========================")
        print("          BUDDY")
        print("========================\n")
        print("1. New Order")
        print("2. View Orders")
        print("3. Search Order")
        print("4. Today's Orders")
        print("5. Today's Summary")
        print("0. Exit")
        print("\n========================\n")

        try:
            choice = int(input("Choose an option: "))
        except ValueError:
            print("\nPlease enter a number.")
            continue

        if choice == 1:
            customer = get_customer()
            order = Order(customer)
            order = take_order(order, products)

            if order is None:
                continue

            order.print_receipt()
            save_order(order)

        elif choice == 2:
            view_orders()

        elif choice == 3:
            search_orders()

        elif choice == 4:
            view_today_orders()

        elif choice == 5:
            view_today_summary()

        elif choice == 0:
            print("\nGoodbye!\n")
            break

        else:
            print("\nInvalid choice. Please try again.")


def run_app():

    products = load_products()

    main_menu(products)


# =========================
# START APPLICATION
# =========================

try:
    run_app()

except Exception as error:
    print("\nSomething went wrong.")
    print("\nPlease restart Buddy.")
    print(f"Error: {error}")
