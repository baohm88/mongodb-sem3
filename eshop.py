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

def add_order():
    orderid = int(input("Enter order ID: "))
    products = []
    while True:
        product_id = input("Enter product ID (or 'done' to finish): ")
        if product_id.lower() == 'done':
            break
        product = product_collection.find_one({"product_id": product_id})
        if not product:
            print("Product not found. Please add it first.")
            continue
        quantity = int(input("Enter quantity: "))
        product_info = {
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "size": product["size"],
            "price": product["price"],
            "quantity": quantity
        }
        products.append(product_info)

    total_amount = sum(p["price"] * p["quantity"] for p in products)
    delivery_address = input("Enter delivery address: ")

    order = {
        "orderid": orderid,
        "products": products,
        "total_amount": total_amount,
        "delivery_address": delivery_address
    }
    order_collection.insert_one(order)
    print("Order added successfully.\n")

def edit_delivery_address():
    orderid = int(input("Enter order ID to update: "))
    new_address = input("Enter new delivery address: ")
    result = order_collection.update_one({"orderid": orderid}, {"$set": {"delivery_address": new_address}})
    if result.matched_count:
        print("Delivery address updated.\n")
    else:
        print("Order not found.\n")

def remove_order():
    orderid = int(input("Enter order ID to remove: "))
    result = order_collection.delete_one({"orderid": orderid})
    if result.deleted_count:
        print("Order removed.\n")
    else:
        print("Order not found.\n")

def view_all_orders():
    orders = order_collection.find()
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


def view_all_products():
    products = product_collection.find()
    table_data = []

    for product in products:
        table_data.append([
            product["product_id"],
            product["product_name"],
            product["size"],
            product["price"]
        ])

    headers = ["Product ID", "Product Name", "Size", "Price"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print()


def main():
    while True:
        print("\n===== E-Shop Order Management =====")
        print("1. Add Product")
        print("2. Add Order")
        print("3. Edit Delivery Address in an Order")
        print("4. Remove an Order")
        print("5. View All Orders")
        print("6. View All Products")
        print("0. Exit")
        
        choice = input("Enter your choice: ")

        if choice == "1":
            add_product()
        elif choice == "2":
            add_order()
        elif choice == "3":
            edit_delivery_address()
        elif choice == "4":
            remove_order()
        elif choice == "5":
            view_all_orders()
        elif choice == "6":
            view_all_products()
        elif choice == "0":
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()
