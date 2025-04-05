from Dao.ordrs import ServiceProvider
from entity.Products import Product
from util.db_conn_util import DBConnUtil
from util.db_property_util import DBPropertyUtil
from exception.dataException import InvalidDataException, ProductNotFoundException

class ProductDAO(ServiceProvider):
    def __init__(self):
        self.__connection_string = DBPropertyUtil.get_connection_string("db.properties")

    def create(self, product):
        query = """ insert into products (productname, description, price, category) 
        values (%s, %s, %s, %s) """
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query, (
                product.product_name,
                product.description,
                product.price,
                product.category
            ))

            cursor.execute("select last_insert_id()")
            product_id = cursor.fetchone()[0]

            cursor.execute("""
                insert into inventory (productid, quantityinstock)
                values (%s, 0)
            """, (product_id,))

            conn.commit()
            return product_id
        except Exception as e:
            conn.rollback()
            if "duplicate key" in str(e).lower():
                raise InvalidDataException("Product name already exists")
            raise Exception(f"Error creating product: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_by_id(self, product_id):
        query = """ select productid, productname, description, price, category
        from products 
        where productid = %s """
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query, (product_id,))
            record = cursor.fetchone()

            if record is None:
                raise ProductNotFoundException(f"Product with ID {product_id} not found")

            return Product(
                product_id=record[0],
                product_name=record[1],
                description=record[2],
                price=record[3],
                category=record[4]
            )

        except Exception as e:
            raise Exception(f"Error retrieving product: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_all(self):
        query = """
        select *
        from products
        """
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query)
            return [
                Product(
                    product_id=row[0],
                    product_name=row[1],
                    description=row[2],
                    price=row[3],
                    category=row[4]
                ) for row in cursor.fetchall()
            ]

        except Exception as e:
            raise Exception(f"Error retrieving products: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def update(self, product):
        query = """ update products 
        set productname = %s, description = %s, price = %s, category = %s
        where productid = %s """
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query, (
                product.product_name,
                product.description,
                product.price,
                product.category,
                product.product_id
            ))

            if cursor.rowcount == 0:
                raise ProductNotFoundException(f"Product with ID {product.product_id} not found")

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            if "duplicate key" in str(e).lower():
                raise InvalidDataException("Product name already exists")
            raise Exception(f"Error updating product: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def delete(self, product_id):
        check_query = "select count(*) from orderdetails where productid = %s"
        delete_query = "delete from products where productid = %s"

        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(check_query, (product_id,))
            if cursor.fetchone()[0] > 0:
                raise InvalidDataException("Cannot delete product with existing orders")

            cursor.execute(delete_query, (product_id,))

            if cursor.rowcount == 0:
                raise ProductNotFoundException(f"Product with ID {product_id} not found")

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            raise Exception(f"Error deleting product: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def search_products(self, id=None, name=None, category=None, min_price=None, max_price=None):
        query = "select * from products where 1=1"
        params = []

        if id:
            query += " and productid = %s"
            params.append(int(id))
        if name:
            query += " and productname like %s"
            params.append(f"%{name}%")
        if category:
            query += " and category = %s"
            params.append(category)
        if min_price is not None:
            query += " and price >= %s"
            params.append(min_price)
        if max_price is not None:
            query += " and price <= %s"
            params.append(max_price)

        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()
            cursor.execute(query, params)

            return [
                Product(
                    product_id=row[0],
                    product_name=row[1],
                    description=row[2],
                    price=row[3],
                    category=row[4]
                ) for row in cursor.fetchall()
            ]
        except Exception as e:
            raise Exception(f"Error searching products: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def check_product_stock(self, product_id):
        conn = None
        cursor = None
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            query = """
            SELECT p.ProductID, p.ProductName, i.QuantityInStock 
            FROM products p
            JOIN inventory i ON p.ProductID = i.ProductID
            WHERE p.ProductID = %s
            """
            cursor.execute(query, (product_id,))
            result = cursor.fetchone()

            if not result:
                raise ProductNotFoundException(f"Product with ID {product_id} not found")

            return {
                'product_id': result[0],
                'product_name': result[1],
                'quantity_in_stock': result[2]
            }

        except Exception as e:
            raise Exception(f"Error checking product stock: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_categories(self):
        query = "select distinct category from products"
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            raise Exception(f"Error getting categories: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()