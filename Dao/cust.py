from Dao.ordrs import ServiceProvider
from entity.Customers import Customer
from util.db_conn_util import DBConnUtil
from util.db_property_util import DBPropertyUtil
from exception.dataException import InvalidDataException, CustomerNotFoundException

class CustomerDAO(ServiceProvider):
    def __init__(self):
        self.__connection_string = DBPropertyUtil.get_connection_string("db.properties")

#________________CRUD Operations____________________
    def create(self, customer):
        query = """insert into customers (firstname,lastname, email,phone, address)
        values (%s, %s, %s, %s, %s)"""
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query, (
                customer.first_name,
                customer.last_name,
                customer.email,
                customer.phone,
                customer.address
            ))

            cursor.execute("select last_insert_id()")
            customer_id = cursor.fetchone()[0]

            conn.commit()
            return customer_id

        except Exception as e:
            conn.rollback()
            if "duplicate key" in str(e).lower():
                raise InvalidDataException("Email already exists")
            raise Exception(f"Error creating customer: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_by_id(self, customer_id, include_order_count=False, order_dao=None):
        query = """select customerid, firstname,lastname,email,phone,address
        from customers
        where customerid= %s"""
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query, (customer_id,))
            record = cursor.fetchone()

            if record is None:
                raise CustomerNotFoundException(f"Customer with ID {customer_id} not found")

            customer = Customer(
                customer_id=record[0],
                first_name=record[1],
                last_name=record[2],
                email=record[3],
                phone=record[4],
                address=record[5]
            )
            if include_order_count and order_dao:
                order_count = order_dao.count_orders_by_customer(customer_id)
                customer.order_count = order_count
            return customer

        except Exception as e:
            raise Exception(f"Error retrieving customer: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_all(self):
        query = """select customerid, firstname,lastname, email, phone, address
        from customers"""
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query)
            records = cursor.fetchall()

            customers = []
            for record in records:
                customer = Customer(
                    customer_id=record[0],
                    first_name=record[1],
                    last_name=record[2],
                    email=record[3],
                    phone=record[4],
                    address=record[5]
                )
                customers.append(customer)
            return customers

        except Exception as e:
            raise Exception(f"Error retrieving customers: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_all_with_order_counts(self, order_dao):
        customers = self.get_all()
        for customer in customers:
            try:
                order_count = order_dao.count_orders_by_customer(customer.customer_id)
                customer.order_count = order_count
            except Exception:
                customer.order_count = 0
        return customers

    def update(self, customer):
        query = """ update customers set firstname= %s, lastname = %s, email=%s, phone= %s, address= %s
        where customerid = %s """
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query, (
                customer.first_name,
                customer.last_name,
                customer.email,
                customer.phone,
                customer.address,
                customer.customer_id
            ))

            if cursor.rowcount == 0:
                raise CustomerNotFoundException(f"Customer with ID {customer.customer_id} not found")

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            if "duplicate key" in str(e).lower():
                raise InvalidDataException("Email already exists")
            raise Exception(f"Error updating customer: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def delete(self, customer_id):
        query = "delete from customers where customerid= %s"
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query, (customer_id,))

            if cursor.rowcount == 0:
                raise CustomerNotFoundException(f"Customer with ID {customer_id} not found")

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            raise Exception(f"Error deleting customer: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_customer_by_email(self, email):
        query = """ select *
        from customers where email = %s """
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query, (email,))
            record = cursor.fetchone()

            if record is None:
                raise CustomerNotFoundException(f"Customer with email {email} not found")

            customer = Customer(
                customer_id=record[0],
                first_name=record[1],
                last_name=record[2],
                email=record[3],
                phone=record[4],
                address=record[5]
            )
            return customer

        except Exception as e:
            raise Exception(f"Error retrieving customer by email: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()