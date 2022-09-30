import csv
from common import yaml_util
import json
import os


def read_csv_file(csv_path: str) -> list:
    """读取数据驱动的csv文件

    Args:
        csv_path (str): csv文件相对项目根目录路径

    Returns:
        list: csv文件数据列表
    """
    with open(yaml_util.get_root_path() + csv_path, encoding="utf8") as f:
        return list(csv.reader(f))


def format_case_data(yaml_case_path: str) -> list:
    """格式测试用例, 使用csv数据驱动的用例初始化

    Args:
        yaml_case_path (str): yaml用例文件相对项目根目录路径

    Returns:
        list: 格式化后的测试用例
    """
    case_data_list = yaml_util.read_case_yaml(yaml_case_path)
    new_case_data_list = []
    # 遍历yaml文件的数组
    for case_data_dict in case_data_list:
        # 判断是否存在parameters节点
        if case_data_dict.get("parameters"):
            # case_data_dict转换为字符串供后续replace
            case_data_str = json.dumps(case_data_dict, ensure_ascii=False)
            # 迭代获取parameters节点下的数据
            for key, value in case_data_dict["parameters"].items():
                # key 需要替换的字段如 name-des-method
                # value 对应的csv路径
                # csv_data_list csv列表数据
                csv_data_list = read_csv_file(value)
                key_list = key.split("-")

                # csv规范，判断csv每行数据个数是否长度一致
                length_flag = True
                for sub_csv_data_list in csv_data_list[1:]:
                    if len(sub_csv_data_list) != len(csv_data_list[0]):
                        print(f"E0002: {sub_csv_data_list} 数据长度有误！！")
                        length_flag = False
                if not length_flag:
                    continue

                # 迭代获取除了csv表头之外的数据
                for sub_csv_data_list in csv_data_list[1:]:
                    temp_case_data_str = case_data_str
                    # col_num列数，从0开始
                    for col_num in range(len(sub_csv_data_list)):
                        # 判断表头的值，是否在需要替换的键内
                        if csv_data_list[0][col_num] in key_list:
                            # 替换数据
                            temp_case_data_str = temp_case_data_str.replace(
                                "$csv{" + csv_data_list[0][col_num] + "}",
                                sub_csv_data_list[col_num])
                            print(">>>>>>>>  temp_case_data_str")
                            print(temp_case_data_str)
                    # 数据替换成功后追加到用例中
                    new_case_data_list.append(json.loads(temp_case_data_str))
                print(">>>>>>>>  csv_data_list")
                print(new_case_data_list)
        else:
            # 不存在parameters节点的时候数据不做处理
            new_case_data_list.append(case_data_dict)

    return new_case_data_list


def get_all_yaml_case_file(module_path) -> list:
    """获取当前py文件下的所有以case_开头yaml用例文件

    Args:
        module_path (str): 模块的__file__值

    Returns:
        list: case_*.yaml文件路径组成的列表
    """
    case_path = os.path.split(module_path)[0]
    folder_content = os.listdir(case_path)
    all_case_file_list = []
    # print(folder_content)
    # return
    for t_file in folder_content:
        if t_file.startswith("case_") and t_file.endswith(".yaml"):
            case_file = case_path + "/" + t_file
            all_case_file_list.append(case_file)
    return all_case_file_list


def format_all_case_data(module_path: str) -> list:
    """当前用例文件夹下的所有测试用例

    Args:
        module_path (str): 用例所在的路径

    Returns:
        list: 所有用例组成的列表
    """
    all_case_data_list = []
    for yaml_case_path in get_all_yaml_case_file(module_path):
        all_case_data_list += format_case_data(yaml_case_path)
    return all_case_data_list


if __name__ == "__main__":
    a = read_csv_file("/data/temp.csv")
    print(a)
