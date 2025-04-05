from entity.Products import Product
from decimal import Decimal
class OrderDetail:
    def __init__(self, order_detail_id, order, product, quantity, unit_price):
        self.__order_detail_id = order_detail_id
        self.__order = order
        self.__product = product
        self.__quantity = quantity
        self.__unit_price = Decimal(str(unit_price)) if not isinstance(unit_price, Decimal) else unit_price
        self.__discount_percentage = Decimal(0)
        self.__subtotal = self.calculate_subtotal()

    @property
    def order_detail_id(self):
        return self.__order_detail_id

    @property
    def order(self):
        return self.__order

    @property
    def product(self):
        return self.__product

    @property
    def quantity(self):
        return self.__quantity

    @property
    def subtotal(self):
        return self.__subtotal

    @quantity.setter
    def quantity(self, value):
        if value <= 0:
            raise ValueError("Quantity must be positive")
        self.__quantity = value
        self.__subtotal = self.calculate_subtotal()

    @property
    def discount_percentage(self):
        return self.__discount_percentage

    @discount_percentage.setter
    def discount_percentage(self, value):
        if not 0 <= value <= 100:
            raise ValueError("Discount must be between 0-100%")
        self.__discount_percentage = value
        self.__subtotal = self.calculate_subtotal()

    @property
    def unit_price(self):
        return self.__unit_price

    def calculate_subtotal(self):
        base_price = self.__unit_price * Decimal(self.__quantity)
        discount_factor = (Decimal(100) - Decimal(self.__discount_percentage)) / Decimal(100)
        return base_price * discount_factor


    def apply_discount(self, percentage):
        if not 0 <= percentage <= 100:
            raise ValueError("Discount must be between 0-100%")
        self.__discount_percentage = percentage
        self.__subtotal = self.calculate_subtotal()