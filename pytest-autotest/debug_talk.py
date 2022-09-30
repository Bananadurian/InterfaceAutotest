import random
from common import yaml_util


class DebugTalk:
    @staticmethod
    def ramdom_num(start: int = 1, end: int = 100) -> int:
        """指定范围内生成一个随机数

        Args:
            start (int, optional): 开始的数. Defaults to 1.
            end (int, optional): 结束的数. Defaults to 100.

        Returns:
            int: 随机数
        """
        return random.randint(int(start), int(end))

    @staticmethod
    def get_extract_data(node: str) -> str:
        """读取extract,yaml文件

        Args:
            node (str): 读取的键

        Returns:
            str: 值
        """
        return yaml_util.read_extract_file(node)

    @staticmethod
    def get_host(host_name: str) -> str:
        """获取config.yaml文件中的host

        Args:
            host_name (str): host名称

        Returns:
            str: host地址
        """
        return yaml_util.read_config_file("host", host_name)