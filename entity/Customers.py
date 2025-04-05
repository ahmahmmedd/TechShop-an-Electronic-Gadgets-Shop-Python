class Customer:
    def __init__(self, customer_id, first_name, last_name, email=None, phone=None, address=None):
        self.__customer_id = customer_id
        self.__orders = []
        self.first_name = first_name
        self.last_name = last_name
        if email is not None:
            self.email = email
        else:
            self.__email = ""

        if phone is not None:
            self.phone = phone
        else:
            self.__phone = ""

        if address is not None:
            self.address = address
        else:
            self.__address = ""

    @property
    def customer_id(self):
        return self.__customer_id

    @property
    def first_name(self):
        return self.__first_name

    @first_name.setter
    def first_name(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("First name must be a non-empty string")
        self.__first_name = value.strip()

    @property
    def last_name(self):
        return self.__last_name

    @last_name.setter
    def last_name(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Last name must be a non-empty string")
        self.__last_name = value.strip()

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        if value == "":  # Allow empty string
            self.__email = value
        elif not self.__validate_email(value):
            raise ValueError("Invalid email format")
        else:
            self.__email = value.strip()

    @property
    def phone(self):
        return self.__phone

    @phone.setter
    def phone(self, value):
        if value == "":
            self.__phone = value
        else:
            self.__phone = value

    @property
    def address(self):
        return self.__address

    @address.setter
    def address(self, value):
        if value == "":
            self.__address = value
        elif not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Address must be a non-empty string")
        else:
            self.__address = value.strip()

    @property
    def orders(self):
        return self.__orders.copy()

    # Validation methods
    def __validate_email(self, email):
        """Basic email validation"""
        if not isinstance(email, str):
            return False
        email = email.strip()
        return ('@' in email and
                '.' in email and
                len(email) > 5 and
                email.count('@') == 1 and
                email[0] != '@' and
                email[-1] != '@')


    def calculate_total_orders(self):
        return len(self.__orders)

    def get_customer_details(self,order_count=None):
        details= (f"Customer ID: {self.__customer_id}\n"
                f"Name: {self.__first_name} {self.__last_name}\n"
                f"Email: {self.__email}\n"
                f"Phone: {self.__phone}\n"
                f"Address: {self.__address}\n")
        if order_count is not None:
            details += f"\nTotal Orders: {order_count}"
        else:
            details += f"\nTotal Orders: {self.calculate_total_orders()}"

        return details

    def update_customer_info(self, first_name=None, last_name=None, email=None, phone=None, address=None):
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone
        if address is not None:
            self.address = address

    def add_order(self, order):
        if order not in self.__orders:
            self.__orders.append(order)

    def remove_order(self, order):
        if order in self.__orders:
            self.__orders.remove(order)