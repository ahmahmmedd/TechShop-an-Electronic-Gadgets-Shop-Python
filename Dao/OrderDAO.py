from Dao.ordrs import ServiceProvider
from decimal import Decimal
from entity.Orders import Order
from entity.Customers import Customer
from entity.Products import Product
from entity.OrderDetails import OrderDetail
from util.db_conn_util import DBConnUtil
from util.db_property_util import DBPropertyUtil
from exception.dataException import (IncompleteOrderException, PaymentFailedException,OrderNotFoundException, InsufficientStockException,ConcurrencyException)

class OrderDAO(ServiceProvider):
    def __init__(self):
        self.__connection_string = DBPropertyUtil.get_connection_string("db.properties")

    def create(self, order):
        conn = None
        cursor = None
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()
            conn.autocommit = False

            order_query = """ insert into orders (customerid, orderdate, totalamount, status)
            values (%s, %s, %s, %s) """
            cursor.execute(order_query, (
                order.customer.customer_id,
                order.order_date,
                order.total_amount,
                order.status
            ))
            order_id = cursor.lastrowid

            for detail in order.order_details:
                stock_query = "select quantityinstock from inventory where productid = %s"
                cursor.execute(stock_query, (detail.product.product_id,))
                stock = cursor.fetchone()[0]

                if stock < detail.quantity:
                    raise InsufficientStockException(
                        f"Not enough stock for {detail.product.product_name}. Available: {stock}"
                    )

                detail_query = """ insert into orderdetails (orderid, productid, quantity, unitprice)
                values (%s, %s, %s, %s) """
                cursor.execute(detail_query, (
                    order_id,
                    detail.product.product_id,
                    detail.quantity,
                    float(detail.product.price)
                ))

                update_query = """ update inventory 
                set quantityinstock = quantityinstock - %s
                where productid = %s """
                cursor.execute(update_query, (
                    detail.quantity,
                    detail.product.product_id
                ))

            payment_query = """ insert into payments (orderid, amount, paymentmethod, status)
            values (%s, %s, %s, %s) """
            payment_status = "Completed" if order.total_amount >0 else "Failed"
            cursor.execute(payment_query, (
                order_id,
                order.total_amount,
                "Credit Card",
                payment_status
            ))

            if payment_status == "Failed":
                raise PaymentFailedException("Payment declined: Amount is not valid")

            conn.commit()
            return order_id


        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def process_payment(self, order_id, payment_method, amount):
        conn = None
        cursor = None
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor(dictionary=True)
            conn.autocommit = False

            order_query = """ 
            select o.TotalAmount, o.Status, c.FirstName AS first_name, c.LastName AS last_name, 
            c.Email AS email, c.Phone AS phone, c.Address AS address
            from orders o
            join customers c ON o.CustomerID = c.CustomerID
            where o.OrderID = %s """
            cursor.execute(order_query, (order_id,))
            order_data = cursor.fetchone()

            if not order_data:
                raise OrderNotFoundException(f"Order with ID {order_id} not found")

            order_amount = Decimal(str(order_data['TotalAmount']))
            order_status = order_data['Status']

            if order_status != 'pending':
                raise PaymentFailedException(f"Cannot process payment for order in {order_status} status")

            balance = amount - order_amount
            if balance < 0:
                raise PaymentFailedException(
                    f"Payment amount ${amount:.2f} is less than order total ${order_amount:.2f}")

            payment_query = """insert into payments (OrderID, Amount, PaymentMethod, Status)
            VALUES (%s, %s, %s, %s)"""
            cursor.execute(payment_query, (
                order_id,
                order_amount,
                payment_method,
                'Completed'
            ))

            if balance > 0:
                cursor.execute(payment_query, (
                    order_id,
                    -balance,
                    'Balance',
                    'Completed'
                ))

            update_query = "UPDATE orders SET Status = 'Paid' WHERE OrderID = %s"
            cursor.execute(update_query, (order_id,))

            conn.commit()

            customer = Customer(
                None,
                order_data['first_name'],
                order_data['last_name'],
                order_data['email'],
                order_data['phone'],
                order_data['address']
            )

            return {
                'order': Order(
                    order_id,
                    customer,
                    None,
                    order_amount,
                    'Paid'
                ),
                'amount_paid': amount,
                'balance_given': balance if balance > 0 else 0
            }

        except Exception as e:
            if conn:
                conn.rollback()
            if isinstance(e, (OrderNotFoundException, PaymentFailedException)):
                raise
            raise Exception(f"Error processing payment: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_payment_details(self, order_id):
        conn = None
        cursor = None
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor(dictionary=True)

            query = """ select p.* 
            from payments p
            where p.orderid = %s
            order by p.orderid
            limit 1 """
            cursor.execute(query, (order_id,))
            payment_data = cursor.fetchone()

            if not payment_data:
                raise PaymentFailedException(f"No payment found for order {order_id}")

            return {
                'payment_id': payment_data['PaymentID'],
                'order_id': payment_data['OrderID'],
                'amount': float(payment_data['Amount']),
                'method': payment_data['PaymentMethod'],
                'status': payment_data['Status']
            }

        except Exception as e:
            if isinstance(e, PaymentFailedException):
                raise
            raise Exception(f"Error retrieving payment details: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def refund_payment(self, order_id, amount=None):
        conn = None
        cursor = None
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()
            conn.autocommit = False

            payment = self.get_payment_details(order_id)
            if payment['status'] != 'Completed':
                raise PaymentFailedException("Cannot refund - payment not completed")

            refund_amount = amount if amount is not None else payment['amount']
            if refund_amount > payment['amount']:
                raise PaymentFailedException(
                    f"Refund amount ${refund_amount} exceeds original payment ${payment['amount']}")

            refund_query = """ insert into payments (orderid, amount, paymentmethod, status)
            values (%s, %s, %s, %s) """
            cursor.execute(refund_query, (
                order_id,
                -refund_amount,
                'Refund',
                'Completed'
            ))

            if refund_amount == payment['amount']:
                update_query = "update orders set status = 'Refunded' where orderid = %s"
                cursor.execute(update_query, (order_id,))

            conn.commit()
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            if isinstance(e, PaymentFailedException):
                raise
            raise Exception(f"Error processing refund: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_by_id(self, order_id):
        conn = None
        cursor = None
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor(dictionary=True)

            order_query = """ 
            SELECT 
                o.OrderID, o.CustomerID, o.OrderDate, o.TotalAmount, o.Status,
                c.FirstName AS first_name, 
                c.LastName AS last_name, 
                c.Email AS email, 
                c.Phone AS phone, 
                c.Address AS address
            FROM orders o
            JOIN customers c ON o.CustomerID = c.CustomerID
            WHERE o.OrderID = %s 
            """
            cursor.execute(order_query, (order_id,))
            order_data = cursor.fetchone()

            if not order_data:
                raise OrderNotFoundException(f"Order with ID {order_id} not found")

            customer = Customer(
                order_data['CustomerID'],
                order_data['first_name'],
                order_data['last_name'],
                order_data['email'],
                order_data['phone'],
                order_data['address']
            )

            order = Order(
                order_data['OrderID'],
                customer,
                order_data['OrderDate'],
                float(order_data['TotalAmount']),
                order_data['Status']
            )

            details_query = """ 
            SELECT 
            od.OrderDetailID, od.ProductID AS productid, 
            od.Quantity AS quantity, od.UnitPrice AS unitprice,
            od.Discount AS discount,
            p.ProductName AS product_name,
            p.Description AS description,
            p.Price AS price,
            p.Category AS category
            FROM orderdetails od
            JOIN products p ON od.ProductID = p.ProductID
            WHERE od.OrderID = %s 
            """
            cursor.execute(details_query, (order_id,))

            for detail_data in cursor.fetchall():
                product = Product(
                    detail_data['productid'],
                    detail_data['product_name'],
                    detail_data['description'],
                    float(detail_data['price']),
                    detail_data['category']
                )

                order_detail = OrderDetail(
                    detail_data['OrderDetailID'],
                    order,
                    product,
                    detail_data['quantity'],
                    float(detail_data['unitprice'])
                )

                if detail_data['discount']:
                    order_detail.apply_discount(float(detail_data['discount']))

                order.add_order_detail(order_detail)

            return order

        except Exception as e:
            raise Exception(f"Error retrieving order: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def update(self, order):
        conn = None
        cursor = None
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()
            conn.autocommit = False

            query = """ update orders 
            set status = %s
            where orderid = %s """
            cursor.execute(query, (
                order.status,
                order.order_id,
            ))

            conn.commit()
            return True

        except ConcurrencyException as e:
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Error updating order: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete(self, order_id):
        conn = None
        cursor = None
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()
            conn.autocommit = False

            details_query = "select productid, quantity from orderdetails where orderid = %s"
            cursor.execute(details_query, (order_id,))
            details = cursor.fetchall()

            for product_id, quantity in details:
                restock_query = """ update inventory 
                set quantityinstock = quantityinstock + %s
                where productid = %s """
                cursor.execute(restock_query, (quantity, product_id))

            delete_query = "delete from orders where orderid = %s"
            cursor.execute(delete_query, (order_id,))

            if cursor.rowcount == 0:
                raise OrderNotFoundException(f"Order with ID {order_id} not found")

            conn.commit()
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_all(self, customer_id=None, status=None, start_date=None, end_date=None):
        conn = None
        cursor = None
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor(dictionary=True)

            query = """ 
            select o.OrderID, o.CustomerID, o.OrderDate, o.TotalAmount, o.Status,
            c.FirstName AS first_name, 
            c.LastName AS last_name
            from orders o
            join customers c ON o.CustomerID = c.CustomerID
            where 1=1 """
            params = []

            if customer_id:
                query += " and o.CustomerID = %s"
                params.append(customer_id)
            if status:
                query += " and o.Status = %s"
                params.append(status)
            if start_date:
                query += " and o.OrderDate >= %s"
                params.append(start_date)
            if end_date:
                query += " and o.OrderDate <= %s"
                params.append(end_date)

            query += " order by o.OrderDate DESC"
            cursor.execute(query, params)

            orders = []
            for order_data in cursor.fetchall():
                customer = Customer(
                    order_data['CustomerID'],
                    order_data['first_name'],
                    order_data['last_name']

                )

                order = Order(
                    order_data['OrderID'],
                    customer,
                    order_data['OrderDate'],
                    float(order_data['TotalAmount']),
                    order_data['Status']
                )
                orders.append(order)

            return orders

        except Exception as e:
            raise Exception(f"Error retrieving orders: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_orders_by_product(self, product_id):
        conn = None
        cursor = None
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor(dictionary=True)

            query = """ select distinct o.*, c.firstname, c.lastname
            from orders o
            join customers c on o.customerid = c.customerid
            join orderdetails od on o.orderid = od.orderid
            where od.productid = %s
            order by o.orderdate desc """
            cursor.execute(query, (product_id,))

            orders = []
            for order_data in cursor.fetchall():
                from entity.Customers import Customer
                customer = Customer(
                    order_data['CustomerID'],
                    order_data['FirstName'],
                    order_data['LastName'],
                    order_data['Email'],
                    order_data['Phone'],
                    order_data['Address']

                )

                from entity.Orders import Order
                orders.append(Order(
                    order_data['OrderID'],
                    customer,
                    order_data['OrderDate'],
                    float(order_data['TotalAmount']),
                    order_data['Status']
                ))

            return orders

        except Exception as e:
            raise Exception(f"Error retrieving orders by product: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def count_orders_by_customer(self, customer_id):
        conn = None
        cursor = None
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            query = "select count(*) from orders where customerid = %s"
            cursor.execute(query, (customer_id,))
            count = cursor.fetchone()[0]

            return count

        except Exception as e:
            raise Exception(f"Error counting orders: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_order_by_detail_id(self, order_detail_id):
        """Get full order by order detail ID"""
        conn = None
        cursor = None
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor(dictionary=True)

            # Get order ID first
            order_id_query = "SELECT orderid FROM orderdetails WHERE orderdetailid = %s"
            cursor.execute(order_id_query, (order_detail_id,))
            order_id_result = cursor.fetchone()

            if not order_id_result:
                raise OrderNotFoundException(f"Order detail with ID {order_detail_id} not found")

            # Then get the full order with proper column aliases
            order_query = """ 
            SELECT 
                o.OrderID, o.CustomerID, o.OrderDate, o.TotalAmount, o.Status,
                c.FirstName AS first_name, 
                c.LastName AS last_name, 
                c.Email AS email, 
                c.Phone AS phone, 
                c.Address AS address
            FROM orders o
            JOIN customers c ON o.CustomerID = c.CustomerID
            WHERE o.OrderID = %s 
            """
            cursor.execute(order_query, (order_id_result['orderid'],))
            order_data = cursor.fetchone()

            if not order_data:
                raise OrderNotFoundException(f"Order with ID {order_id_result['orderid']} not found")

            customer = Customer(
                order_data['CustomerID'],
                order_data['first_name'],
                order_data['last_name'],
                order_data['email'],
                order_data['phone'],
                order_data['address']
            )

            order = Order(
                order_data['OrderID'],
                customer,
                order_data['OrderDate'],
                float(order_data['TotalAmount']),
                order_data['Status']
            )

            # Get order details with proper column aliases
            details_query = """ 
            SELECT 
                od.OrderDetailID, od.ProductID AS productid, 
                od.Quantity AS quantity, od.UnitPrice AS unitprice,
                od.Discount AS discount,
                p.ProductName AS product_name,
                p.Description AS description,
                p.Price AS price,
                p.Category AS category
            FROM orderdetails od
            JOIN products p ON od.ProductID = p.ProductID
            WHERE od.OrderID = %s 
            """
            cursor.execute(details_query, (order_data['OrderID'],))

            for detail_data in cursor.fetchall():
                product = Product(
                    detail_data['productid'],
                    detail_data['product_name'],
                    detail_data['description'],
                    float(detail_data['price']),
                    detail_data['category']
                )

                order_detail = OrderDetail(
                    detail_data['OrderDetailID'],
                    order,
                    product,
                    detail_data['quantity'],
                    float(detail_data['unitprice'])
                )

                if detail_data['discount']:
                    order_detail.apply_discount(float(detail_data['discount']))

                order.add_order_detail(order_detail)

            return order

        except Exception as e:
            raise Exception(f"Error retrieving order by detail ID: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def update_order_detail_quantity(self, order_detail_id, new_quantity):

        conn = None
        cursor = None
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()
            conn.autocommit = False

            get_query = """select productid, quantity, orderid 
                          from orderdetails where orderdetailid = %s"""
            cursor.execute(get_query, (order_detail_id,))
            detail = cursor.fetchone()

            if not detail:
                raise OrderNotFoundException(f"Order detail with ID {order_detail_id} not found")

            product_id, old_quantity, order_id = detail
            quantity_diff = new_quantity - old_quantity


            stock_query = "select quantityinstock from inventory where productid = %s"
            cursor.execute(stock_query, (product_id,))
            stock = cursor.fetchone()[0]

            if quantity_diff > stock:
                raise InsufficientStockException(
                    f"Not enough stock. Available: {stock}, Needed: {quantity_diff}")

            update_detail_query = """update orderdetails 
                                   set quantity = %s 
                                   where orderdetailid = %s"""
            cursor.execute(update_detail_query, (new_quantity, order_detail_id))

            update_inventory_query = """update inventory 
                                      set quantityinstock = quantityinstock - %s 
                                      where productid = %s"""
            cursor.execute(update_inventory_query, (quantity_diff, product_id))

            update_order_query = """update orders o
                                  set totalamount = (
                                  select sum(quantity * unitprice) 
                                  from orderdetails 
                                  where orderid = o.orderid)
                                  where orderid = %s"""
            cursor.execute(update_order_query, (order_id,))

            conn.commit()
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def apply_discount_to_order_detail(self, order_detail_id, discount_percentage):
        conn = None
        cursor = None
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()
            conn.autocommit = False


            verify_query = "select orderid from orderdetails where orderdetailid = %s"
            cursor.execute(verify_query, (order_detail_id,))
            result = cursor.fetchone()

            if not result:
                raise OrderNotFoundException(f"Order detail with ID {order_detail_id} not found")

            order_id = result[0]
            update_query = """update orderdetails 
                             set discount = %s 
                             where orderdetailid = %s"""
            cursor.execute(update_query, (discount_percentage, order_detail_id))

            update_order_query = """update orders o
                                  set totalamount = (
                                  select sum(quantity * unitprice * (1 - COALESCE(discount,0)/100)) 
                                  from orderdetails 
                                  where orderid = o.orderid)
                                  where orderid = %s"""
            cursor.execute(update_order_query, (order_id,))

            conn.commit()
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()