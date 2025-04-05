import logging
from datetime import datetime
import os
from exception.dataException import LoggingException


class LoggerUtil:
    _instance = None

    def __new__(cls, log_file="techshop.log"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_logger(log_file)
        return cls._instance

    def init_logger(self, log_file):
        try:
            os.makedirs("logs", exist_ok=True)

            self.logger = logging.getLogger("TechShop")
            self.logger.setLevel(logging.DEBUG)
            file_handler = logging.FileHandler(f"logs/{log_file}")
            file_handler.setLevel(logging.DEBUG)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        except Exception as e:
            raise LoggingException(f"Failed to initialize logger: {str(e)}")

    def log_error(self, message):
        self.logger.error(message, exc_info=True)

    def log_info(self, message):
        self.logger.info(message)

    def log_debug(self, message):
        self.logger.debug(message)

    def log_warning(self, message):
        self.logger.warning(message)