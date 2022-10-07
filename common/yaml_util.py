import yaml
import os


def get_root_path():
    """获取工作目录路径

    Returns:
        str: 获取common的上级目录路径, 避免以脚本运行的时候找不到对应的文件
    """
    path = os.getcwd().split("common")[0]
    return path


def read_config_file(first_node: str, second_node: str) -> str:
    """读取config.yaml内容

    Args:
        first_node (str): 第一个节点
        second_node (str): 第二个节点

    Returns:
        str: 对应节点的值
    """
    with open(get_root_path() + "/config.yaml", encoding="utf8") as f:
        res = yaml.load(stream=f, Loader=yaml.FullLoader)
    return res[first_node][second_node]


def write_extract_file(data: str) -> None:
    """追加方式往extract,yaml文件写入内容

    Args:
        data (str): 写入的字典
    """
    with open(get_root_path() + "/extract.yaml", "a", encoding="utf8") as f:
        yaml.dump(data=data, stream=f, allow_unicode=True)


def read_extract_file(node: str) -> str:
    """读取extract,yaml文件

    Args:
        node (str): 读取的键

    Returns:
        str: 值
    """
    with open(get_root_path() + "/extract.yaml", encoding="utf8") as f:
        res = yaml.load(stream=f, Loader=yaml.FullLoader)
    return res[node]  # 会存在TypeError: 'NoneType' object is not subscriptable


def clear_extract_file() -> None:
    """清空extract,yaml文件
    """
    with open(get_root_path() + "/extract.yaml", "w") as f:
        # w的文件指针在开头，所以可以清空内容
        f.truncate()


def read_case_yaml(yaml_file_path: str) -> list:
    """读取yaml用例文件

    Args:
        yaml_file_path (str): 用例文件的绝对路径

    Returns:
        list: 数据列表 [{}, {}]
    """
    with open(yaml_file_path, encoding="utf8") as f:
        data = yaml.load(stream=f, Loader=yaml.FullLoader)
    return data


if __name__ == "__main__":
    # print(read_config_file("host", "baidu"))
    print(read_case_yaml())

# print(os.getcwd().split("common")[0])