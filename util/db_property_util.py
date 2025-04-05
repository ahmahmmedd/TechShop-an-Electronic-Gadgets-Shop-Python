import configparser
import os
from exception.dataException import DatabaseConnectionException

class DBPropertyUtil:
    @staticmethod
    def get_connection_string(property_file_name):
        try:
            config = configparser.ConfigParser()
            prop_file_path = os.path.join(os.path.dirname(__file__), '..', property_file_name)

            if not os.path.exists(prop_file_path):
                raise FileNotFoundError(f"Property file {property_file_name} not found at {prop_file_path}")

            config.read(prop_file_path)

            if 'database' not in config:
                raise ValueError("Invalid property file format - missing [database] section")

            db_config = config['database']
            required_keys = ['host', 'database', 'user', 'password']

            if not all(key in db_config for key in required_keys):
                raise ValueError("Missing required database configuration (host/database/user/password)")

            return (
                f"host={db_config['host']} "
                f"dbname={db_config['database']} "
                f"user={db_config['user']} "
                f"password={db_config['password']} "
                f"port={db_config.get('port', '3306')}"
            )

        except Exception as e:
            raise DatabaseConnectionException(f"Error reading property file: {str(e)}")