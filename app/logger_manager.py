import logging


class LoggerManager:
    def __init__(self, logger_name: str, log_file: str, logger_lvl: str) -> None:
        self.logger_name = logger_name
        self.log_file = log_file
        self.logger_lvl = logger_lvl

    def logger_setup(self) -> logging.Logger:
        """настраиваем логгер что бы создавать по нему экземпляры"""
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(self.logger_lvl)

        logger.propagate = False

        if not logger.handlers:
            file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
            file_handler.setLevel(self.logger_lvl)

            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)

            logger.addHandler(file_handler)

        return logger


global_logger = LoggerManager(
    logger_name="global_log", log_file="global_logger.log", logger_lvl="DEBUG"
)
exceptions_logger = LoggerManager(
    logger_name="exception_log", log_file="exception_logger.log", logger_lvl="ERROR"
)
transfer_logger = LoggerManager(
    logger_name="transfer_log", log_file="transfer_logger.log", logger_lvl="INFO"
)

global_logger = global_logger.logger_setup()
exceptions_logger = exceptions_logger.logger_setup()
transfer_logger = transfer_logger.logger_setup()
