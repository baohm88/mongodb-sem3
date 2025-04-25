from pymongo import MongoClient
from tabulate import tabulate

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["eShop"]
order_collection = db["orders"]
product_collection = db["products"]

def add_product():
    product = {
        "product_id": input("Enter product ID: "),
        "product_name": input("Enter product name: "),
        "size": input("Enter product size: "),
        "price": float(input("Enter product price: ")),
    }
    product_collection.insert_one(product)
    print("Product added successfully.\n")

def view_all_products():
    products = list(product_collection.find())
    if not products:
        print("⚠️  No products found.\n")
        return

    table_data = [
        [product["product_id"], product["product_name"], product["size"], product["price"]]
        for product in products
    ]
    headers = ["Product ID", "Product Name", "Size", "Price"]
    print("\n📦 All Products:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print(f"\n📊 Total Products: {len(products)}\n")


def delete_product():
    products = list(product_collection.find())
    if not products:
        print("⚠️  No products found.\n")
        return

    table_data = [
        [product["product_id"], product["product_name"], product["size"], product["price"]]
        for product in products
    ]
    headers = ["Product ID", "Product Name", "Size", "Price"]
    print("\n🗑️  Available Products to Delete:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    product_id = input("\nEnter the Product ID to delete: ").strip()
    result = product_collection.delete_one({"product_id": product_id})

    if result.deleted_count:
        print(f"✅ Product '{product_id}' deleted successfully.\n")
    else:
        print("❌ Product not found or already deleted.\n")

def edit_product():
    products = list(product_collection.find())
    if not products:
        print("⚠️  No products found.\n")
        return

    table_data = [
        [product["product_id"], product["product_name"], product["size"], product["price"]]
        for product in products
    ]
    headers = ["Product ID", "Product Name", "Size", "Price"]
    print("\n✏️  Available Products to Edit:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    product_id = input("\nEnter the Product ID to edit: ").strip()
    product = product_collection.find_one({"product_id": product_id})
    if not product:
        print("❌ Product not found.\n")
        return

    new_product_id = input(f"Enter new Product ID [{product['product_id']}]: ") or product['product_id']
    new_name = input(f"Enter new name [{product['product_name']}]: ") or product['product_name']
    new_size = input(f"Enter new size [{product['size']}]: ") or product['size']
    new_price = input(f"Enter new price [{product['price']}]: ") or product['price']

    try:
        new_price = float(new_price)
    except ValueError:
        print("❌ Invalid price entered. Edit cancelled.\n")
        return

    # Check if new_product_id already exists (and is not the same product)
    if new_product_id != product['product_id']:
        existing = product_collection.find_one({"product_id": new_product_id})
        if existing:
            print("❌ A product with that Product ID already exists. Edit cancelled.\n")
            return

    update = {
        "product_id": new_product_id,
        "product_name": new_name,
        "size": new_size,
        "price": new_price
    }
    product_collection.update_one({"product_id": product_id}, {"$set": update})
    print("✅ Product updated successfully.\n")


def add_order():
    # Step 1: Auto-generate order ID
    last_order = order_collection.find_one(sort=[("orderid", -1)])
    new_orderid = (last_order["orderid"] + 1) if last_order else 1

    # Step 2: Show all available products
    all_products = list(product_collection.find())
    if not all_products:
        print("⚠️  No products available. Please add products first.\n")
        return

    print("\n🛒 Available Products:")
    product_table = [[p["product_id"], p["product_name"], p["size"], p["price"]] for p in all_products]
    headers = ["Product ID", "Product Name", "Size", "Price"]
    print(tabulate(product_table, headers=headers, tablefmt="grid"))

    # Step 3: Let user choose products to order
    products = []
    while True:
        product_id = input("\nEnter product ID to add to order (or 'done' to finish): ").strip()
        if product_id.lower() == 'done':
            break

        product = product_collection.find_one({"product_id": product_id})
        if not product:
            print("❌ Product not found. Try again.")
            continue

        quantity = int(input(f"Enter quantity for '{product['product_name']}': "))
        products.append({
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "size": product["size"],
            "price": product["price"],
            "quantity": quantity
        })

    if not products:
        print("⚠️  No products selected. Order was not created.\n")
        return

    total_amount = sum(p["price"] * p["quantity"] for p in products)
    delivery_address = input("Enter delivery address: ")

    order = {
        "orderid": new_orderid,
        "products": products,
        "total_amount": total_amount,
        "delivery_address": delivery_address
    }

    order_collection.insert_one(order)
    print(f"\n✅ Order #{new_orderid} created successfully!")

    # 🎉 Show the newly created order
    print(f"\n📦 New Order Details:")
    print(f"Order ID: {order['orderid']}")
    print(f"Delivery Address: {order['delivery_address']}")

    table_data = []
    for idx, product in enumerate(order["products"], start=1):
        total = product["price"] * product["quantity"]
        table_data.append([
            idx,
            product["product_name"],
            product["price"],
            product["quantity"],
            total
        ])

    headers = ["No", "Product Name", "Price", "Quantity", "Total"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print(f"\n💰 Total Amount: {order['total_amount']}\n")


def view_all_orders():
    orders = list(order_collection.find())
    if not orders:
        print("⚠️  No orders found.\n")
        return

    for order in orders:
        print(f"\n📦 Order ID: {order['orderid']}")
        print(f"🚚 Delivery Address: {order['delivery_address']}")
        print()

        table_data = []
        for idx, product in enumerate(order["products"], start=1):
            total = product["price"] * product["quantity"]
            table_data.append([
                idx,
                product["product_name"],
                product["price"],
                product["quantity"],
                total
            ])

        headers = ["No", "Product Name", "Price", "Quantity", "Total"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\n💰 Total Amount: {order['total_amount']}\n")

    print(f"📊 Total Orders: {len(orders)}\n")

def edit_order():
    orders = list(order_collection.find())

    if not orders:
        print("⚠️  No orders found.\n")
        return

    # Show all existing orders first
    table_data = [[order["orderid"], order["total_amount"], order["delivery_address"]] for order in orders]
    headers = ["Order ID", "Total Amount", "Delivery Address"]
    print("\n📝 Existing Orders:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    try:
        orderid = int(input("\nEnter the Order ID to edit: "))
        order = order_collection.find_one({"orderid": orderid})
        if not order:
            print("❌ Order not found.\n")
            return
    except ValueError:
        print("❌ Invalid input. Please enter a valid Order ID.\n")
        return

    # Allow user to update delivery address
    new_address = input(f"Enter new delivery address [{order['delivery_address']}]: ") or order['delivery_address']

    # Allow user to update product quantities
    updated_products = []
    print("\n🛠️  Edit Quantities:")
    for product in order["products"]:
        print(f"{product['product_name']} (Current quantity: {product['quantity']})")
        try:
            qty_input = input("New quantity (or press Enter to keep current): ").strip()
            new_qty = int(qty_input) if qty_input else product["quantity"]
        except ValueError:
            print("❌ Invalid quantity. Keeping original.")
            new_qty = product["quantity"]

        updated_product = product.copy()
        updated_product["quantity"] = new_qty
        updated_products.append(updated_product)

    # Recalculate total
    new_total = sum(p["price"] * p["quantity"] for p in updated_products)

    # Update the order in DB
    result = order_collection.update_one(
        {"orderid": orderid},
        {"$set": {
            "delivery_address": new_address,
            "products": updated_products,
            "total_amount": new_total
        }}
    )

    if result.modified_count:
        print("✅ Order updated successfully!\n")
    else:
        print("⚠️  No changes made.\n")

    # 🎉 Show the updated order
    print(f"\n📦 Updated Order #{orderid}")
    print(f"🚚 Delivery Address: {new_address}")
    table_data = []
    for idx, product in enumerate(updated_products, start=1):
        total = product["price"] * product["quantity"]
        table_data.append([
            idx,
            product["product_name"],
            product["price"],
            product["quantity"],
            total
        ])
    headers = ["No", "Product Name", "Price", "Quantity", "Total"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print(f"\n💰 Total Amount: {new_total}\n")



def main():
    while True:
        print("\n===== E-Shop Order Management =====")
        print("1. Add a Product")
        print("2. View all Products")
        print("3. Delete a Product")
        print("4. Edit a Product")
        print("5. Add an Order")
        print("6. View all Orders")
        print("7. Edit an Order")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_product()
        elif choice == "2":
            view_all_products()
        elif choice == "3":
            delete_product()
        elif choice == "4":
            edit_product()
        elif choice == "5":
            add_order()
        elif choice == "6":
            view_all_orders()
        elif choice == "7":
            edit_order()
        elif choice == "0":
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()
