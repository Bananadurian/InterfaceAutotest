import logging
import logging.handlers
import datetime
from common import yaml_util
# import yaml_util


class LogUtil:
    logger = logging.getLogger("test.log")

    def create_logger(self):
        # 设置全局等级
        self.logger.setLevel(logging.DEBUG)
        log_path = yaml_util.get_root_path() + "/logs/"
        log_name = yaml_util.read_config_file("log", "name")

        # 判断是否已经存在handles，已经存在不处理
        if not self.logger.handlers:
            # 创建一个支持时间切割的handlers,凌晨切割
            rf_handler = logging.handlers.TimedRotatingFileHandler(
                log_path + log_name,
                when='midnight',
                interval=1,
                backupCount=7,
                atTime=datetime.time(0, 0, 0, 0),
                encoding="utf8")
            # 设置等级
            log_level = yaml_util.read_config_file("log", "level").upper()
            log_level_conf = {
                "DEBUG": logging.DEBUG,
                "INFO": logging.INFO,
                "WARNING": logging.WARNING,
                "ERROR": logging.ERROR,
                "CRITICAL": logging.CRITICAL
            }
            if log_level_conf.get(log_level):
                rf_handler.setLevel(log_level_conf[log_level])

            # 设置格式
            log_format = yaml_util.read_config_file("log", "fomat")
            rf_handler.setFormatter(logging.Formatter(log_format))

            self.logger.addHandler(rf_handler)
        return self.logger


def write_log(msg: str, level: str = "INFO") -> None:
    logger = LogUtil().create_logger()
    logger_level_conf = {
        "DEBUG": logger.debug,
        "INFO": logger.info,
        "WARNING": logger.warning,
        "ERROR": logger.error,
        "CRITICAL": logger.critical
    }
    level = level.upper()
    if logger_level_conf.get(level):
        logger_level_conf[level](msg)
    else:
        logger.info(msg)


def error_log(msg: str, level: str = "ERROR") -> None:
    logger = LogUtil().create_logger()
    logger_level_conf = {
        "DEBUG": logger.debug,
        "INFO": logger.info,
        "WARNING": logger.warning,
        "ERROR": logger.error,
        "CRITICAL": logger.critical
    }
    level = level.upper()
    if logger_level_conf.get(level):
        logger_level_conf[level](msg)
    else:
        logger.error(msg)
    raise Exception(msg)


if __name__ == "__main__":
    logger = LogUtil().create_logger()
    logger.info("dsfsff")
