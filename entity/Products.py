class Product:
    def __init__(self, product_id, product_name, description, price, category):
        self.__product_id = product_id
        self.__product_name = product_name
        self.__description = description
        self.__price = price
        self.__category = category

    @property
    def product_id(self):
        return self.__product_id

    @property
    def product_name(self):
        return self.__product_name

    @product_name.setter
    def product_name(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Product name must be a non-empty string")
        self.__product_name = value.strip()

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = value

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, value):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Price must be a non-negative number")
        self.__price = value

    @property
    def category(self):
        return self.__category

    @category.setter
    def category(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Category must be a non-empty string")
        self.__category = value.strip()

    def get_product_details(self):
        return (f"Product ID: {self.__product_id}\n"
                f"Name: {self.__product_name}\n"
                f"Category: {self.__category}\n"
                f"Description: {self.__description}\n"
                f"Price: {self.__price}")

    def update_product_info(self, product_name=None, description=None, price=None, category=None):
        if product_name is not None:
            self.product_name = product_name
        if description is not None:
            self.description = description
        if price is not None:
            self.price = price
        if category is not None:
            self.category = category