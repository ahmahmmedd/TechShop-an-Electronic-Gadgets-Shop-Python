import mysql.connector
from exception.dataException import DatabaseConnectionException


class DBConnUtil:
    @staticmethod
    def get_connection(connection_string):
        try:
            params = {}
            for item in connection_string.split():
                if '=' in item:
                    key, value = item.split('=', 1)
                    params[key] = value

            conn = mysql.connector.connect(
                host=params['host'],
                database=params['dbname'],
                user=params['user'],
                password=params['password'],
                port=params.get('port', '3306')
            )
            return conn

        except mysql.connector.Error as e:
            raise DatabaseConnectionException(f"MySQL Connection Error: {str(e)}")