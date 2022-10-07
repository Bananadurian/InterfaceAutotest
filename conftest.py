import pytest
from common import yaml_util
from common import log_util


@pytest.fixture(scope="session", autouse=False)
def clear_extract_file():
    """执行用例前清空文件内容
    """
    # print("清理extract.yaml文件")
    log_util.write_log("清理extract.yaml文件内容")
    yaml_util.clear_extract_file()


# @pytest.fixture(scope="session", autouse=True)
# def get_logger():
#     print(">>>>>> logger创建 >>>>>>>")
#     return log_util.LogUtil().create_logger()
