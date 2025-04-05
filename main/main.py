from util.db_conn_util import DBConnUtil
from util.db_property_util import DBPropertyUtil
from Dao.cust import CustomerDAO
from Dao.ProductDAO import ProductDAO
from Dao.OrderDAO import OrderDAO
from Dao.InventoryDAO import InventoryDAO
from entity.Customers import Customer
from entity.Products import Product
from entity.Orders import Order
from exception.dataException import (InvalidDataException,CustomerNotFoundException,ProductNotFoundException,
                                     IncompleteOrderException, PaymentFailedException,InsufficientStockException,
                                     OrderNotFoundException)


def display_main_menu():
    print("\n=== TechShop Management System ===")
    print("1. Customer Management")
    print("2. Product Management")
    print("3. Order Management")
    print("4. Inventory Management")
    print("5. Exit")


# ========== CUSTOMER MANAGEMENT ==========
def display_customer_menu():
    print("\n------ Customer Management ------")
    print("1. Add New Customer")
    print("2. View Customer Details")
    print("3. Update Customer Information")
    print("4. Delete Customer")
    print("5. List All Customers")
    print("6. Back to Main Menu")


def customer_management(customer_dao,order_dao):
    while True:
        display_customer_menu()
        choice = input("\nEnter your choice (1-6): ")

        if choice == '1':
            add_customer(customer_dao)
        elif choice == '2':
            view_customer(customer_dao,order_dao)
        elif choice == '3':
            update_customer(customer_dao)
        elif choice == '4':
            delete_customer(customer_dao)
        elif choice == '5':
            list_all_customers(customer_dao,order_dao)
        elif choice == '6':
            break
        else:
            print("\nInvalid choice. Enter a number between 1-6.")


# ========== PRODUCT MANAGEMENT ==========
def display_product_menu():
    print("\n--- Product Management ---")
    print("1. Add New Product")
    print("2. View Product Details")
    print("3. Update Product Information")
    print("4. Delete Product")
    print("5. List All Products")
    print("6. Search Products")
    print("7. Check Product Stock")
    print("8. Back to Main Menu")


def product_management(product_dao):
    while True:
        display_product_menu()
        choice = input("\nEnter your choice (1-7): ")

        if choice == '1':
            add_product(product_dao)
        elif choice == '2':
            view_product(product_dao)
        elif choice == '3':
            update_product(product_dao)
        elif choice == '4':
            delete_product(product_dao)
        elif choice == '5':
            list_products(product_dao)
        elif choice == '6':
            search_products(product_dao)
        elif choice == '7':
            check_product_stock(product_dao)
        elif choice == '8':
            break
        else:
            print("\nInvalid choice. Enter number between 1-8.")

# ========== ORDER MANAGEMENT ==========
def order_management(order_dao, customer_dao, product_dao):
    while True:
        print("\n-------- Order Management -----------")
        print("1. Place New Order")
        print("2. View Order Details")
        print("3. Update Order Status")
        print("4. Update Order Item Quantity")
        print("5. Apply Discount to Order Item")
        print("6. Cancel an Order")
        print("7. List All Orders")
        print("8. Payment Management")
        print("9. Return to Main Menu")

        choice = input("\nEnter your choice (1-8): ")

        if choice == '1':
            place_order(order_dao, customer_dao, product_dao)
        elif choice == '2':
            view_order(order_dao)
        elif choice == '3':
            update_order_status(order_dao)
        elif choice == '4':
            update_order_item_quantity(order_dao)
        elif choice == '5':
            apply_discount_to_item(order_dao)
        elif choice == '6':
            cancel_order(order_dao)
        elif choice == '7':
            list_orders(order_dao)
        elif choice == '8':
            payment_management(order_dao)
        elif choice == '9':
            break
        else:
            print("\nInvalid choice. Enter a number between 1-7.")

# ========= Inventory MAnagement=======
def inventory_management(inventory_dao, product_dao):
    while True:
        print("\n---------- Inventory Management ------------")
        print("1. View Product Stock")
        print("2. Add Stock")
        print("3. Remove Stock")
        print("4. Set Stock Quantity")
        print("5. Search Inventory")
        print("6. List Low Stock Items")
        print("7. Back to Main Menu")

        choice = input("\nEnter your choice (1-7): ")

        if choice == '1':
            view_stock(inventory_dao, product_dao)
        elif choice == '2':
            update_stock(inventory_dao, "add")
        elif choice == '3':
            update_stock(inventory_dao, "remove")
        elif choice == '4':
            update_stock(inventory_dao, "set")
        elif choice == '5':
            search_inventory(inventory_dao, product_dao)
        elif choice == '6':
            list_low_stock(inventory_dao, product_dao)
        elif choice == '7':
            break
        else:
            print("\nInvalid choice. Please enter a number between 1-7.")

#============Payment Management================
def payment_management(order_dao):
    while True:
        print("\n--- Payment Management ---")
        print("1. Process Payment")
        print("2. View Payment Details")
        print("3. Process Refund")
        print("4. Back to Order Management")

        choice = input("\nEnter your choice (1-4): ")

        if choice == '1':
            process_payment(order_dao)
        elif choice == '2':
            view_payment_details(order_dao)
        elif choice == '3':
            process_refund(order_dao)
        elif choice == '4':
            break
        else:
            print("\nInvalid choice. Please enter a number between 1-4.")


def process_payment(order_dao):
    print("\n[Process Payment]")
    try:
        order_id = int(input("Enter Order ID: "))
        payment_method = input("Payment Method (Credit/Debit/PayPal): ")
        amount = float(input("Payment Amount: "))

        result = order_dao.process_payment(order_id, payment_method, amount)
        order = result['order']

        print(f"\nPayment processed successfully for Order - {order.order_id}!")
        print(f"Customer: {order.customer.first_name} {order.customer.last_name}")
        print(f"Order Total: AED{order.total_amount:.2f}")
        print(f"Amount Paid: AED{result['amount_paid']:.2f}")

        if result['balance_given'] > 0:
            print(f"Balance Given: AED{result['balance_given']:.2f}")

        print(f"New Status: {order.status}")

    except ValueError:
        print("\nInvalid input. Enter a valid Number!")
    except OrderNotFoundException as e:
        print(f"\nError: {str(e)}")
    except PaymentFailedException as e:
        print(f"\nPayment Error: {str(e)}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")

def view_payment_details(order_dao):
    print("\n[View Payment Details]")
    try:
        order_id = int(input("Enter Order ID: "))
        payment = order_dao.get_payment_details(order_id)

        print("\nPayment Details:")
        print("-" * 50)
        print(f"Payment ID: {payment['payment_id']}")
        print(f"Order ID: {payment['order_id']}")
        print(f"Amount: AED{payment['amount']:.2f}")
        print(f"Method: {payment['method']}")
        print(f"Status: {payment['status']}")

    except ValueError:
        print("\nInvalid input. Please enter a numeric Order ID.")
    except PaymentFailedException as e:
        print(f"\nError: {str(e)}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")


def process_refund(order_dao):
    print("\n[Process Refund]")
    try:
        order_id = int(input("Enter Order ID: "))
        amount_input = input("Refund Amount (leave blank for full refund): ")
        amount = float(amount_input) if amount_input else None

        if order_dao.refund_payment(order_id, amount):
            print("\n Refund processed successfully!")

    except ValueError:
        print("\nInvalid input. Please enter valid numbers.")
    except PaymentFailedException as e:
        print(f"\nRefund Error: {str(e)}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")

# ========== CUSTOMER OPERATIONS ==========
def add_customer(customer_dao):
    print("\n[Add New Customer]")
    try:
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        email = input("Email: ")
        phone = input("Phone: ")
        address = input("Address: ")

        customer = Customer(None, first_name, last_name, email, phone, address)
        customer_id = customer_dao.create(customer)
        print(f"\nCustomer created successfully. ID- {customer_id}")
    except InvalidDataException as e:
        print(f"\nError: {str(e)}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")


def view_customer(customer_dao,order_dao):
    print("\n[View Customer Details]")
    customer_id = int(input("Enter Customer ID: "))
    try:
        customer = customer_dao.get_by_id(customer_id, include_order_count=True, order_dao=order_dao)
        order_count = order_dao.count_orders_by_customer(customer_id)
        print(customer.get_customer_details(order_count))
    except CustomerNotFoundException as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def update_customer(customer_dao):
    print("\n[Update Customer Information]")
    try:
        customer_id = int(input("Enter Customer ID to update: "))
        customer = customer_dao.get_by_id(customer_id)

        print("\nCurrent Details:")
        print(customer.get_customer_details())

        print("\nEnter new details (leave blank to keep current):")
        first_name = input(f"First Name [{customer.first_name}]: ") or customer.first_name
        last_name = input(f"Last Name [{customer.last_name}]: ") or customer.last_name
        email = input(f"Email [{customer.email}]: ") or customer.email
        phone = input(f"Phone [{customer.phone}]: ") or customer.phone
        address = input(f"Address [{customer.address}]: ") or customer.address

        updated_customer = Customer(
            customer_id,
            first_name,
            last_name,
            email,
            phone,
            address
        )

        if customer_dao.update(updated_customer):
            print("\n Customer updated successfully!")
    except CustomerNotFoundException as e:
        print(f"\n Error: {str(e)}")
    except InvalidDataException as e:
        print(f"\n Error: {str(e)}")
    except ValueError:
        print("\n Invalid input. Please enter a numeric Customer ID.")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")


def delete_customer(customer_dao):
    print("\n[Delete Customer]")
    try:
        customer_id = int(input("Enter Customer ID to delete: "))
        if customer_dao.delete(customer_id):
            print("\n Customer deleted successfully!")
    except CustomerNotFoundException as e:
        print(f"\n Error: {str(e)}")
    except InvalidDataException as e:
        print(f"\n Error: {str(e)}")
    except ValueError:
        print("\n Invalid input. Please enter a numeric Customer ID.")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")

def view_customer_details(customer_dao, order_dao):
    customer_id = int(input("Enter Customer ID: "))
    try:
        customer = customer_dao.get_by_id(customer_id, include_order_count=True, order_dao=order_dao)
        order_count = order_dao.count_orders_by_customer(customer_id)
        print(customer.get_customer_details(order_count))
    except CustomerNotFoundException as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def list_all_customers(customer_dao,order_dao):
    print("\n[List All Customers]")
    try:
        customers = customer_dao.get_all_with_order_counts(order_dao)
        if not customers:
            print("No customers found.")
            return

        print("\nID\tName\t\t\tEmail\t\t\tOrders")
        print("-" * 80)
        for customer in customers:
            print(f"{customer.customer_id}\t"
                  f"{customer.first_name} {customer.last_name[:15]:<20}\t"
                  f"{customer.email[:20]:<20}\t"
                  f"{customer.order_count}")

    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")


# ========== PRODUCT OPERATIONS ==========
def add_product(product_dao):
    print("\n[Add New Product]")
    try:
        name = input("Product Name: ")
        description = input("Description: ")
        price = float(input("Price: "))
        category = input("Category: ")

        product = Product(
            product_id=None,
            product_name=name,
            description=description,
            price=price,
            category=category
        )

        product_id = product_dao.create(product)
        print(f"\n Product created successfully! ID: {product_id}")
    except ValueError:
        print("\n Invalid input. Please enter valid numbers for price.")
    except InvalidDataException as e:
        print(f"\n Error: {str(e)}")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")


def view_product(product_dao):
    print("\n[View Product Details]")
    try:
        product_id = int(input("Enter Product ID: "))
        product = product_dao.get_by_id(product_id)
        stock_info = product_dao.check_product_stock(product_id)

        print("\nProduct Details:")
        print(product.get_product_details())
        print(f"Current Stock: {stock_info['quantity_in_stock']}")

    except ProductNotFoundException as e:
        print(f"\n Error: {str(e)}")
    except ValueError:
        print("\n Invalid input. Please enter a numeric Product ID.")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")


def update_product(product_dao):
    print("\n[Update Product Information]")
    try:
        product_id = int(input("Enter Product ID to update: "))
        product = product_dao.get_by_id(product_id)

        print("\nCurrent Details:")
        print(product.get_product_details())

        print("\nEnter new details (leave blank to keep current):")
        name = input(f"Name [{product.product_name}]: ") or product.product_name
        description = input(f"Description [{product.description}]: ") or product.description
        price = input(f"Price [{product.price}]: ")
        price = float(price) if price else product.price
        category = input(f"Category [{product.category}]: ") or product.category

        updated_product = Product(
            product_id,
            name,
            description,
            price,
            category
        )

        if product_dao.update(updated_product):
            print("\n Product updated successfully!")
    except ValueError:
        print("\n Invalid input. Please enter valid numbers for price.")
    except ProductNotFoundException as e:
        print(f"\n Error: {str(e)}")
    except InvalidDataException as e:
        print(f"\n Error: {str(e)}")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")


def delete_product(product_dao):
    print("\n[Delete Product]")
    try:
        product_id = int(input("Enter Product ID to delete: "))

        if product_dao.delete(product_id):
            print("\n Product deleted successfully!")
    except ValueError:
        print("\n Invalid input. Please enter a numeric Product ID.")
    except ProductNotFoundException as e:
        print(f"\n Error: {str(e)}")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")


def list_products(product_dao):
    print("\n[List All Products]")
    try:
        products = product_dao.get_all()
        if not products:
            print("No products found.")
            return

        print("\nID\tName\tDescription\tCategory\tPrice")
        print("-" * 60)
        for product in products:
            print(
                f"{product.product_id}\t{product.product_name[:15]:<15}\t{product.description[:30]:<30}\t{product.category[:15]:<25}\t{product.price}")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")


def check_product_stock(product_dao):
    print("\n[Check Product Stock]")
    try:
        product_id = int(input("Enter Product ID to check stock: "))
        stock_info = product_dao.check_product_stock(product_id)

        print("\nProduct Stock Information:")
        print(f"Product ID: {stock_info['product_id']}")
        print(f"Product Name: {stock_info['product_name']}")
        print(f"Quantity in Stock: {stock_info['quantity_in_stock']}")

    except ValueError:
        print("\nInvalid input. Please enter a valid Product ID.")
    except ProductNotFoundException as e:
        print(f"\nError: {str(e)}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")

def search_products(product_dao):
    print("\n[Search Products]")
    try:
        print("Leave field blank to ignore it")
        id= input("Product id:")
        name = input("Product name contains: ")
        category = input("Category: ")
        min_price = input("Minimum price: ")
        max_price = input("Maximum price: ")

        products = product_dao.search_products(
            id= id if id else None,
            name=name if name else None,
            category=category if category else None,
            min_price=float(min_price) if min_price else None,
            max_price=float(max_price) if max_price else None
        )

        if not products:
            print("No products match your criteria.")
            return

        print("\nSearch Results:")
        print("ID\tName\t\tCategory\tPrice")
        print("-" * 50)
        for product in products:
            print(
                f"{product.product_id}\t{product.product_name[:15]:<15}\t{product.category[:15]:<15}\t{product.price}")

    except ValueError:
        print("\n Invalid input. Please enter valid numbers for prices.")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")

#============Order Management=================

def place_order(order_dao, product_dao, customer_dao):
    print("\n[Place New Order]")
    try:

        customer_id = int(input("Enter Customer ID: "))
        customer = customer_dao.get_by_id(customer_id)

        from entity.Orders import Order
        order = Order(None, customer)

        while True:
            print("\nCurrent Order:")
            print(f"Items: {len(order.order_details)}")
            print(f"Total: AED{order.total_amount:.2f}")
            print("\n1. Add Product")
            print("2. Finalize Order")
            choice = input("Select option: ")

            if choice == '1':
                product_id = int(input("Enter Product ID: "))
                product = product_dao.get_by_id(product_id)
                quantity = int(input("Enter Quantity: "))

                from entity.OrderDetails import OrderDetail
                order_detail = OrderDetail(
                    None,
                    order,
                    product,
                    quantity,
                    product.price
                )
                order.add_order_detail(order_detail)

                print(f"Added {quantity}x {product.product_name} at AED {product.price:.2f} each")
                print(f"Item subtotal: AED {order_detail.subtotal:.2f}")


            elif choice == '2':
                if not order.order_details:
                    print("Cannot place empty order")
                    continue
                break
            else:
                print("Invalid choice")

        order_id = order_dao.create(order)
        print(f"\n Order placed successfully! Order ID: {order_id}")

    except ValueError:
        print("\n Invalid input. Please enter valid numbers.")
    except IncompleteOrderException as e:
        print(f"\n Error: {str(e)}")
    except PaymentFailedException as e:
        print(f"\n Payment failed: {str(e)}")
        print("Please try again with a different payment method")
    except InsufficientStockException as e:
        print(f"\n Error: {str(e)}")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")


def view_order(order_dao):
    print("\n[View Order Details]")
    try:
        order_id = int(input("Enter Order ID: "))
        order = order_dao.get_by_id(order_id)
        print("\n" + order.get_order_details())
    except OrderNotFoundException as e:
        print(f"\n Error: {str(e)}")
    except ValueError:
        print("\n Invalid input. Please enter a numeric Order ID.")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")


def update_order_status(order_dao):
    print("\n[Update Order Status]")
    try:
        order_id = int(input("Enter Order ID: "))
        order = order_dao.get_by_id(order_id)

        print("\nCurrent Status:", order.status)
        print("\nAvailable statuses: Pending, Processing, Shipped, Delivered, Cancelled")
        new_status = input("Enter new status: ").capitalize()

        order.status = new_status
        if order_dao.update(order):
            print("\n Order status updated successfully!")
    except ValueError as e:
        print(f"\n Error: {str(e)}")
    except OrderNotFoundException as e:
        print(f"\n Error: {str(e)}")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")


def update_order_item_quantity(order_dao):
    print("\n[Update Order Item Quantity]")
    try:

        order_detail_id = int(input("Enter Order Detail ID to update: "))
        order = order_dao.get_order_by_detail_id(order_detail_id)
        order_detail = None
        for detail in order.order_details:
            if detail.order_detail_id == order_detail_id:
                order_detail = detail
                break

        if not order_detail:
            raise OrderNotFoundException("Order detail not found in order")

        print(f"\nCurrent Product: {order_detail.product.product_name}")
        print(f"Current Quantity: {order_detail.quantity}")
        new_quantity = int(input("Enter new quantity: "))
        if new_quantity <= 0:
            raise ValueError("Quantity must be positive")

        if order_dao.update_order_detail_quantity(order_detail_id, new_quantity):
            print("\nOrder item quantity updated successfully!")

    except ValueError:
        print("\nInvalid input. Please enter valid numbers.")
    except OrderNotFoundException as e:
        print(f"\nError: {str(e)}")
    except InsufficientStockException as e:
        print(f"\nError: {str(e)}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")


def apply_discount_to_item(order_dao):
    print("\n[Apply Discount to Order Item]")
    try:
        order_detail_id = int(input("Enter Order Detail ID to discount: "))
        order = order_dao.get_order_by_detail_id(order_detail_id)
        order_detail = None
        for detail in order.order_details:
            if detail.order_detail_id == order_detail_id:
                order_detail = detail
                break

        if not order_detail:
            raise OrderNotFoundException("Order detail not found in order")

        print(f"\nCurrent Product: {order_detail.product.product_name}")
        print(f"Current Price: {order_detail.unit_price}")
        print(f"Current Quantity: {order_detail.quantity}")
        print(f"Current Subtotal: {order_detail.subtotal}")
        discount = float(input("Enter discount percentage (0-100): "))
        if order_dao.apply_discount_to_order_detail(order_detail_id, discount):
            print("\nDiscount applied successfully!")
            print(f"New subtotal: {order_detail.unit_price * order_detail.quantity * (1 - discount / 100):.2f}")

    except ValueError:
        print("\nInvalid input. Please enter valid numbers.")
    except OrderNotFoundException as e:
        print(f"\nError: {str(e)}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")

def cancel_order(order_dao):
    print("\n[Cancel Order]")
    try:
        order_id = int(input("Enter Order ID to cancel: "))

        order = order_dao.get_by_id(order_id)
        print("\nOrder to cancel:")
        print(order.get_order_details())

        confirm = input("\nAre you sure you want to cancel this order? (y/n): ").lower()
        if confirm != 'y':
            print("Order cancellation aborted.")
            return

        if order_dao.delete(order_id):
            print("\n Order cancelled successfully. Inventory has been restocked.")

    except OrderNotFoundException as e:
        print(f"\n Error: {str(e)}")
    except ValueError:
        print("\n Invalid input. Please enter a numeric Order ID.")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")


def list_orders(order_dao):
    print("\n[List Orders]")
    try:
        print("\nFilter options (leave blank to ignore):")
        customer_id = input("Customer ID: ")
        status = input("Status (Pending/Processing/Shipped/Delivered/Cancelled/Paid/Refunded): ").capitalize()
        start_date = input("Start date (YYYY-MM-DD): ")
        end_date = input("End date (YYYY-MM-DD): ")

        customer_id = int(customer_id) if customer_id else None
        status = status if status in ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"] else None
        start_date = start_date if start_date else None
        end_date = end_date if end_date else None

        orders = order_dao.get_all(
            customer_id=customer_id,
            status=status,
            start_date=start_date,
            end_date=end_date
        )

        if not orders:
            print("\nNo orders found matching your criteria.")
            return

        print("\nID\tCustomer\t\tDate\t\tStatus\t\tTotal")
        print("-" * 80)
        for order in orders:
            customer_name = f"{order.customer.first_name} {order.customer.last_name}"
            print(
                f"{order.order_id}\t{customer_name[:25]:<25}\t{order.order_date.strftime('%Y-%m-%d')}\t{order.status[:10]:<10}\tAED{order.total_amount:.2f}")

    except ValueError:
        print("\nInvalid input. Enter valid Customer ID.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")


def search_orders(order_dao):
    print("\n[Search Orders]")
    try:
        print("\nSearch by:")
        print("1. Product")
        print("2. Date Range")
        print("3. Order Total Range")
        search_type = input("Enter search type (1-3): ")

        if search_type == '1':
            product_id = int(input("Enter Product ID: "))
            orders = order_dao.get_orders_by_product(product_id)

        elif search_type == '2':
            start_date = input("Start date (YYYY-MM-DD): ")
            end_date = input("End date (YYYY-MM-DD): ")
            orders = order_dao.get_all(start_date=start_date, end_date=end_date)

        elif search_type == '3':

            min_amount = float(input("Minimum order total: "))
            max_amount = float(input("Maximum order total: "))

            conn = DBConnUtil.get_connection(DBPropertyUtil.get_connection_string("db.properties"))
            cursor = conn.cursor(dictionary=True)

            query = """
            SELECT o.*, c.FirstName, c.LastName 
            FROM Orders o
            JOIN Customers c ON o.CustomerID = c.CustomerID
            WHERE o.TotalAmount BETWEEN %s AND %s
            ORDER BY o.OrderDate DESC
            """
            cursor.execute(query, (min_amount, max_amount))

            orders = []
            for order_data in cursor.fetchall():
                from entity.Customers import Customer
                customer = Customer(
                    order_data['CustomerID'],
                    order_data['FirstName'],
                    order_data['LastName'],
                    "", "", ""
                )
                orders.append(Order(
                    order_data['OrderID'],
                    customer,
                    order_data['OrderDate'],
                    float(order_data['TotalAmount']),
                    order_data['Status']
                ))

        else:
            print("\n Invalid search type.")
            return

        if not orders:
            print("\nNo orders found matching your criteria.")
            return

        print("\nSearch Results:")
        print("ID\tCustomer\t\tDate\t\tStatus\t\tTotal")
        print("-" * 80)
        for order in orders:
            customer_name = f"{order.customer.first_name} {order.customer.last_name}"
            print(
                f"{order.order_id}\t{customer_name[:25]:<25}\t{order.order_date.strftime('%Y-%m-%d')}\t{order.status[:10]:<10}\tAED{order.total_amount:.2f}")

    except ValueError:
        print("\n Invalid input. Please enter valid numbers.")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")

#===========INVENTory+================
def view_stock(inventory_dao, product_dao):
    print("\n[View Product Stock]")
    try:
        product_id = int(input("Enter Product ID: "))
        product = product_dao.get_by_id(product_id)
        stock = inventory_dao.get_stock(product_id)

        print("\nProduct Details:")
        print(f"ID: {product.product_id}")
        print(f"Name: {product.product_name}")
        print(f"Category: {product.category}")
        print(f"Current Stock: {stock}")

    except ValueError:
        print("\n Invalid input. Please enter a numeric Product ID.")
    except ProductNotFoundException as e:
        print(f"\n Product not found: {str(e)}")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")


def update_stock(inventory_dao, action_type):
    actions = {
        "add": ("add to", 1),
        "remove": ("remove from", -1),
        "set": ("set", 0)
    }

    print(f"\n[{action_type.capitalize()} Stock]")
    try:
        product_id = int(input("Enter Product ID: "))

        if action_type == "set":
            new_quantity = int(input("Enter new stock quantity: "))
            inventory_dao.set_stock(product_id, new_quantity)
            print(f" Stock set to {new_quantity}")
        else:
            quantity = int(input(f"Amount to {actions[action_type][0]} stock: "))
            if action_type == "remove":
                current_stock = inventory_dao.get_stock(product_id)
                if quantity > current_stock:
                    raise InsufficientStockException("Cannot remove more than current stock")

            inventory_dao.update_stock(product_id, quantity * actions[action_type][1])
            print(f" Stock updated. New quantity: {inventory_dao.get_stock(product_id)}")

    except ValueError:
        print("\n Invalid input. Please enter valid numbers.")
    except InsufficientStockException as e:
        print(f"\n Error: {str(e)}")
    except ProductNotFoundException as e:
        print(f"\n Product not found: {str(e)}")
    except Exception as e:
        print(f"\n An unexpected error occurred: {str(e)}")


def list_low_stock(inventory_dao, threshold=5):
    print("\n[Low Stock Items]")
    try:
        threshold = int(input(f"Enter low stock threshold (5): "))
        items = inventory_dao.get_low_stock_items(threshold)

        if not items:
            print(f"\nNo products with stock below {threshold}")
            return

        print(f"\nProducts with stock below {threshold}:")
        print("-" * 80)
        print(f"{'ID':<5}{'Product':<25}{'Category':<20}{'Stock':>10}{'Updated':>20}")
        print("-" * 80)

        for item in items:
            print(f"{item['ProductID']:<5}"
                  f"{item['ProductName'][:24]:<25}"
                  f"{item['Category'][:19]:<20}"
                  f"{item['Quantity']:>10}"
                  f"{str(item['LastUpdated'])[:16]:>20}")

    except ValueError:
        print("\nInvalid input. Please enter a valid number.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")


def search_inventory(inventory_dao, product_dao):
    print("\n[Search Inventory]")
    try:
        print("Leave field blank to ignore it")
        product_id = input("Product ID: ")
        product_name = input("Product name contains: ")
        min_stock = input("Minimum stock quantity: ")
        max_stock = input("Maximum stock quantity: ")
        low_stock_only = input("Show low stock only (y/n): ").lower() == 'y'

        results = inventory_dao.search_inventory(
            product_id=int(product_id) if product_id else None,
            product_name=product_name if product_name else None,
            min_stock=int(min_stock) if min_stock else None,
            max_stock=int(max_stock) if max_stock else None,
            low_stock_only=low_stock_only
        )

        if not results:
            print("\nNo inventory items match your criteria.")
            return

        print("\nSearch Results:")
        print("-" * 100)
        print(f"{'ProductID':<10}{'Product Name':<25}{'Category':<20}{'Stock':<10}{'Last Updated':<20}")
        print("-" * 100)

        for item in results:
            print(f"{item['ProductID']:<10}"
                  f"{item['ProductName'][:24]:<25}"
                  f"{item['Category'][:19]:<20}"
                  f"{item['QuantityInStock']:<10}"
                  f"{str(item['LastStockUpdate'])[:16]:<20}")

    except ValueError:
        print("\nInvalid input. Please enter valid numbers for ID and quantities.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")



# ========== MAIN FUNCTION ==========
def main():
    customer_dao = CustomerDAO()
    product_dao = ProductDAO()
    order_dao = OrderDAO()
    inventory_dao = InventoryDAO()


    while True:
        display_main_menu()
        choice = input("\nEnter your choice (1-5): ")

        if choice == '1':
            customer_management(customer_dao,order_dao)
        elif choice == '2':
            product_management(product_dao)
        elif choice == '3':
            order_management(order_dao,product_dao, customer_dao)
        elif choice == '4':
            inventory_management(inventory_dao,product_dao)
        elif choice == '5':
            print("\nThank you for using TechShop Management System. Goodbye!")
            break
        else:
            print("\n Invalid choice. Please enter a number between 1-5.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user.")
    except Exception as e:
        print(f"\n A critical error occurred: {str(e)}")