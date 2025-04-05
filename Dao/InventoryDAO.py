from Dao.ordrs import ServiceProvider
from util.db_conn_util import DBConnUtil
from util.db_property_util import DBPropertyUtil
from exception.dataException import InvalidDataException, InsufficientStockException, ProductNotFoundException

class InventoryDAO(ServiceProvider):
    def __init__(self):
        self.__connection_string = DBPropertyUtil.get_connection_string("db.properties")

    def create(self, inventory_item):
        query = """ insert into inventory (productid, quantityinstock) 
        values (%s, %s) """
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query, (
                inventory_item['product_id'],
                inventory_item['quantity']
            ))

            cursor.execute("select last_insert_id()")
            inventory_id = cursor.fetchone()[0]
            conn.commit()
            return inventory_id
        except Exception as e:
            conn.rollback()
            if "foreign key constraint" in str(e).lower():
                raise ProductNotFoundException("Product does not exist")
            raise Exception(f"Error creating inventory record: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_by_id(self, inventory_id):
        query = """
        select i.inventoryid, i.productid, p.productname, p.category, i.quantityinstock, i.laststockupdate 
        from inventory i
        join products p on i.productid = p.productid
        where i.inventoryid = %s """
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor(dictionary=True)

            cursor.execute(query, (inventory_id,))
            record = cursor.fetchone()

            if not record:
                raise Exception(f"Inventory record {inventory_id} not found")

            return {
                'inventory_id': record['InventoryID'],
                'product_id': record['ProductID'],
                'product_name': record['ProductName'],
                'category': record['Category'],
                'quantity': record['QuantityInStock'],
                'last_updated': record['LastStockUpdate']
            }
        except Exception as e:
            raise Exception(f"Error retrieving inventory: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_all(self):
        query = """ select i.inventoryid, i.productid, p.productname, p.category, i.quantityinstock, i.laststockupdate 
        from inventory i
        join products p on i.productid = p.productid """
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor(dictionary=True)

            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error retrieving inventory: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def update(self, inventory_item):
        query = """ update inventory 
        set productid = %s, quantityinstock = %s 
        where inventoryid = %s """
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query, (
                inventory_item['product_id'],
                inventory_item['quantity'],
                inventory_item['inventory_id']
            ))

            if cursor.rowcount == 0:
                raise Exception("No inventory record was updated")

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error updating inventory: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def delete(self, inventory_id):
        query = "delete from inventory where inventoryid = %s"
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query, (inventory_id,))

            if cursor.rowcount == 0:
                raise Exception("No inventory record was deleted")

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error deleting inventory: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_stock(self, product_id):
        query = """ select quantityinstock 
        from inventory 
        where productid = %s """
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query, (product_id,))
            result = cursor.fetchone()

            if not result:
                raise ProductNotFoundException(f"No inventory record for product {product_id}")

            return result[0]
        except Exception as e:
            raise Exception(f"Error getting stock: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def update_stock(self, product_id, quantity_change):
        query = """ update inventory 
        set quantityinstock = quantityinstock + %s,
        laststockupdate = current_timestamp
        where productid = %s """
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            if quantity_change < 0:
                current_stock = self.get_stock(product_id)
                if current_stock + quantity_change < 0:
                    raise InsufficientStockException(
                        f"Cannot remove {-quantity_change} units. Only {current_stock} available."
                    )

            cursor.execute(query, (quantity_change, product_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error updating stock: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def set_stock(self, product_id, new_quantity):
        if new_quantity < 0:
            raise InvalidDataException("Stock quantity cannot be negative")

        query = """update inventory set quantityinstock = %s,
        laststockupdate = current_timestamp
        where productid = %s """
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor()

            cursor.execute(query, (new_quantity, product_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error setting stock: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def search_inventory(self, product_id=None, product_name=None,
                         min_stock=None, max_stock=None, low_stock_only=False):
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor(dictionary=True)

            query = """select i.ProductID, p.ProductName, p.Category, i.QuantityInStock, i.LastStockUpdate
            from Inventory i
            join Products p ON i.ProductID = p.ProductID
            where 1=1 """
            params = []

            # Build query dynamically
            if product_id:
                query += " AND i.ProductID = %s"
                params.append(product_id)

            if product_name:
                query += " AND p.ProductName LIKE %s"
                params.append(f"%{product_name}%")

            if min_stock is not None:
                query += " AND i.QuantityInStock >= %s"
                params.append(min_stock)

            if max_stock is not None:
                query += " AND i.QuantityInStock <= %s"
                params.append(max_stock)

            if low_stock_only:
                query += " AND i.QuantityInStock < 5"  # Assuming 5 is low stock threshold

            cursor.execute(query, params)
            return cursor.fetchall()

        except Exception as e:
            raise Exception(f"Error searching inventory: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_low_stock_items(self, threshold=5):
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor(dictionary=True)

            query = """
            select p.ProductID, p.ProductName, p.Category, i.QuantityInStock AS Quantity, i.LastStockUpdate AS LastUpdated
            from Inventory i
            join Products p ON i.ProductID = p.ProductID
            where i.QuantityInStock <= %s
            order by i.QuantityInStock """
            cursor.execute(query, (threshold,))
            return cursor.fetchall()

        except Exception as e:
            raise Exception(f"Error getting low stock items: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def _execute_inventory_search(self, query, params):
        try:
            conn = DBConnUtil.get_connection(self.__connection_string)
            cursor = conn.cursor(dictionary=True)

            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error searching inventory: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()