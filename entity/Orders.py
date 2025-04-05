from datetime import datetime
from decimal import Decimal
from entity.Customers import Customer
from exception.dataException import IncompleteOrderException


class Order:
    def __init__(self, order_id, customer, order_date=None, total_amount=0.0, status="Pending",version= 1):
        self.__order_id = order_id
        self.__customer = customer  # Composition with Customer
        self.__order_date = order_date if order_date else datetime.now()
        self.__total_amount = total_amount
        self.__status = status
        self.__order_details = []
        self.__version = version

    @property
    def version(self):
        return self.__version

    # Getters
    @property
    def order_id(self):
        return self.__order_id

    @property
    def customer(self):
        return self.__customer

    @property
    def order_date(self):
        return self.__order_date

    @property
    def total_amount(self):
        return self.__total_amount

    @property
    def status(self):
        return self.__status

    @property
    def order_details(self):
        return self.__order_details.copy()

    @status.setter
    def status(self, value):
        valid_statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
        if value not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        self.__status = value

    def add_order_detail(self, order_detail):
        self.__order_details.append(order_detail)
        self.__total_amount = float(sum(Decimal(str(detail.subtotal)) for detail in self.__order_details))

    def calculate_total_amount(self):
        return float(sum(Decimal(str(detail.subtotal)) for detail in self.__order_details))

    def get_order_details(self):
        details = f"Order #{self.__order_id}\n"
        details += f"Customer: {self.__customer.first_name} {self.__customer.last_name}\n"
        details += f"Date: {self.__order_date.strftime('%Y-%m-%d %H:%M')}\n"
        details += f"Status: {self.__status}\n"
        details += f"Total: AED{self.__total_amount:.2f}\n\n"
        details += "Items:\n"
        for detail in self.__order_details:
            details += (f"Product Name:{detail.product.product_name}\n Quantity: {detail.quantity} \n"
                        f"Product Price: AED {detail.product.price:.2f}\n AED {detail.calculate_subtotal():.2f}\n")
        return details