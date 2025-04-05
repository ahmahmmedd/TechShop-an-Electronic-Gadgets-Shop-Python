class InvalidDataException(Exception):
    """Raised when invalid data is provided"""
    pass

class InsufficientStockException(Exception):
    """Raised when there's not enough stock for a product"""
    pass

class IncompleteOrderException(Exception):
    """Raised when order details are incomplete"""
    pass

class PaymentFailedException(Exception):
    """Raised when payment processing fails"""
    pass

class DatabaseConnectionException(Exception):
    """Raised when there's a database connection issue"""
    pass

class PaymentFailedException(Exception):
    """Raised when payment processing fails"""
    pass

class OrderNotFoundException(Exception):
    """Raised when order is not found"""
    pass

class InsufficientStockException(Exception):
    """Raised when not enough stock is available"""
    pass

class CustomerNotFoundException(Exception):
    """Raised when a customer is not found in the database"""
    pass
class ProductNotFoundException(Exception):
    """RAised when a product is not found in the database"""

class LoggingException(Exception):
    """Raised when a there is an error in log entry """

class AuthenticationException(Exception):
    """Raised when authentication fails"""
    pass

class AuthorizationException(Exception):
    """Raised when authorization fails"""
    pass

class ConcurrencyException(Exception):
    """Raised when concurrent modification is detected"""
    pass
class SqlException(Exception):
    """Raised when there is an error in sql query"""
    pass