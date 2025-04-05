from datetime import datetime


class Inventory:
    def __init__(self, inventory_id, product, quantity_in_stock):
        self.__inventory_id = inventory_id
        self.__product = product
        self.__quantity_in_stock = quantity_in_stock
        self.__last_stock_update = datetime.now()

    def get_product(self):
        return self.__product

    def get_quantity_in_stock(self):
        return self.__quantity_in_stock

    def add_to_inventory(self, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.__quantity_in_stock += quantity
        self.__update_stock_time()

    def remove_from_inventory(self, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > self.__quantity_in_stock:
            raise ValueError("Insufficient stock")
        self.__quantity_in_stock -= quantity
        self.__update_stock_time()

    def is_product_available(self, quantity_to_check):
        return self.__quantity_in_stock >= quantity_to_check

    def __update_stock_time(self):
        self.__last_stock_update = datetime.now()