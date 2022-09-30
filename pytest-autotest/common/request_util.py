import requests
from common import yaml_util
from common import log_util
import json
import re
import debug_talk
import jsonpath


class RequestUtil:
    s = requests.Session()  # 共享请求的session对象，会话保持得以cookie共享

    def replace_value(self, data):
        """替换{{dfsdf}}的内容,已废弃使用函数热加载方法replace_load

        Args:
            data (str|dict): 替换的数据

        Returns:
            str|dict: 替换后的数据
        """
        # 这里的data可能是参数的url，也可能是params、headers、data,json
        if data and isinstance(data, dict):
            str_data = json.dumps(data, ensure_ascii=False)  # 字典转换为字符串
        elif data and isinstance(data, str):
            str_data = data  # 不处理
        for i in range(str_data.count("{{")):
            if "{{" in str_data and "}}" in str_data:
                # 这里可以用正则去匹配出分组，然后通过分组的span()去取索引
                start_index = str_data.index("{{")  # 第一个{{索引
                end_index = str_data.index("}}", start_index)  # 第一个}}索引
                old_value = str_data[start_index:end_index + 2]  # 根据索引取值
                new_value = yaml_util.read_extract_file(
                    old_value[2:-2])  # 根据键获取yaml文件的值
                str_data = str_data.replace(old_value, new_value)  # 替换

        if isinstance(data, dict):
            # print(f">>>>>>>>>>>str_data\n{str_data}")
            data = json.loads(str_data)  # 转换回字典
            # print(f">>>>>>>>>>>data\n{data}")
        else:
            data = str_data  # 不处理
        return data

    def replace_load(self, data) -> str or dict:
        """热加载函数, 把yaml文件中的${get_extract_data(access_token)}替换为对应函数的返回值

        Args:
            data (str | dict): 处理的参数

        Raises:
            Exception: 数据类型不是 str | dict的时候报错

        Returns:
            str or dict: 处理后的数据
        """
        if isinstance(data, dict):
            str_data = json.dumps(data, ensure_ascii=False)
        elif isinstance(data, str):
            str_data = data
        else:
            raise Exception(f"{data} 的数据类型是{type(data)},不是 str | dict")

        match_obj = re.findall(r"\${.*?}", str_data)  # 正则匹配使用了${xx()}的地方
        for t_func_name in match_obj:
            # 函数名
            func_name = re.findall(r"\${(.*?)\(", t_func_name)[0]
            # 函数参数
            temp_func_args_list = re.findall(r".*?\((.*?)\)", t_func_name)
            if temp_func_args_list:
                func_args_list = []
                # 分割参数 11, 22
                temp_func_args_list = temp_func_args_list[0].split(",")
                # 处理参数之间 , 存在空格问题
                for arg in temp_func_args_list:
                    func_args_list.append(arg.strip())
            # 通过反射调取
            func = getattr(debug_talk.DebugTalk, func_name)
            # print(f">>>>>>处理后的参数: {func_args_list}")
            result = func(*func_args_list)
            # 返回值不是字符串的时候，需要转为字符串
            str_data = str_data.replace(t_func_name, str(result))

        if isinstance(data, dict):
            data = json.loads(str_data)  # 字典转为字符串
        elif isinstance(data, str):
            data = str_data
        return data

    def extract_handle(self, res_text: str, extract_data_dict: dict) -> None:
        """保存需要供后续接口使用的数据, 如token

        Args:
            res_text (str): 接口响应的数据
            extract_data_dict (dict): yaml测试用例extract节点下的字典
        """
        for key, value in extract_data_dict.items():
            # 通过正则提取，正则判断有缺陷
            if "(.*?)" in value or "(.+?)" in value:
                pat = re.compile(value)
                match_obj = pat.search(res_text)
                if match_obj:
                    # 写入文件
                    yaml_util.write_extract_file({key: match_obj.group(1)})
                    log_util.write_log(
                        f"extract.yaml通过正则写入{key}: {match_obj.group(1)}")
            # 通过json提取，也有缺陷
            else:
                res_json = json.loads(res_text)
                # 写入文件
                if res_json.get(value):
                    yaml_util.write_extract_file({key: res_json[value]})
                    log_util.write_log(
                        f"extract.yaml通过json写入{key}: {match_obj.group(1)}")

    def assert_data(self, expected_results: list,
                    response_obj: object) -> None:
        """结果断言

        Args:
            expected_results (list): 断言数据
            response_obj (object): 响应的response对象
        """
        assert_flag = 0  # 是否成功标记
        assert_msg = ""
        # 迭代yaml文件中的validata节点下的断言数据
        for validata in expected_results:
            # 判断字典的键是否是 equals
            if list(validata.keys()) == ["equals"]:
                # 状态码断言处理
                if list(validata["equals"].keys()) == ["status_code"]:
                    if response_obj.status_code != validata["equals"][
                            "status_code"]:
                        assert_flag += 1
                        assert_msg += f"""E0001: status_code断言失败, 预期结果:{validata["equals"]["status_code"]}, 实际结果: {response_obj.status_code}\n"""
                # 非状态码断言处理
                else:
                    t_key = list(validata["equals"].keys())[0]
                    # 通过jsonpath获取对应节点的数据,为空的时候返回 false,存在对应数据的时候是一个值组成的列表
                    json_node = jsonpath.jsonpath(response_obj.json(),
                                                  f"$..{t_key}")
                    if json_node:
                        # 判断断言中的值是否在列表中
                        if validata["equals"][t_key] not in json_node:
                            assert_flag += 1
                            assert_msg += f"""E0002: {t_key}断言失败, 预期结果:{validata["equals"][t_key]}, 实际结果: 列表{json_node} 中不存在 {validata["equals"][t_key]}\n"""
                    else:
                        assert_flag += 1
                        assert_msg += f"""E0003: {t_key}断言失败, 响应结果中不存在 {t_key}"""
            # 判断字典的键是contains
            elif list(validata.keys()) == ["contains"]:
                # 判断节点contains的值是否存在响应结果中
                if validata["contains"] not in response_obj.text:
                    assert_flag += 1
                    assert_msg += f"""E0004: {validata["contains"]}断言失败, 响应结果中不存在 {validata["contains"]}"""
            else:
                assert_flag += 1
                assert_msg += f"""W0001: 断言失败, 未支持的断言方式：{list(validata.keys())}"""
        return assert_flag, assert_msg

    def analysis_yaml(self, case_data: dict):
        """处理yaml用例数据,并发起请求

        Args:
            case_data (dict): 用例字典数据

        Returns:
            (Response, assert_flag, assert_msg) | str: 
            正常发出请求的时候返回Response对象、断言结果、断言message组成的元组, 未发出请求的时候返回缺失的节点信息,
        """
        try:
            # 校验yaml文件是否存在必要的键，不存在报KeyError
            case_data["name"]
            case_data["host"]
            case_data["request"]
            case_data["validata"]
            # 如果对应数据提取后，把数据删除，保留未提取的数据传给请求方法
            url_path = case_data["request"].pop("url_path")
            url = case_data["host"] + url_path
            method = case_data["request"].pop("method")
            # 处理请求头
            headers = None
            if case_data["request"].get("headers"):
                headers = case_data["request"].pop("headers")
            # 处理文件
            files = None
            if case_data["request"].get("files"):
                files = case_data["request"].pop("files")

            res = self.send_request(case_name=case_data["name"],
                                    method=method,
                                    url=url,
                                    headers=headers,
                                    files=files,
                                    **case_data["request"])

            # 处理需要提取的数据，比如token
            if case_data.get("extract"):
                self.extract_handle(res.text, case_data["extract"])

            # 断言结果
            assert_flag, assert_msg = self.assert_data(case_data["validata"],
                                                       res)
            return res, assert_flag, assert_msg

        except KeyError as e:
            # e 是错误对象，调用的时候调用了__str__方法
            res = f"yaml文件不存在或位置错误: {e}"
            # print(res)
            # 统一返回一个元组，避免调用的地方由于接收参数数量不对报错
            return res, None, None
        except Exception as e:
            log_util.error_log(e)

    def send_request(self, case_name: str, method: str, url: str, **kwargs):
        """发送请求获取Response

        Args:
            case_name(str): 用例名称
            method (str): 请求方法
            url_path (str): 请求的(Resource Path)资源路径

        Returns:
            class: Response
        """
        method = method.lower()  # 防止大写问题

        # 处理url、params、data、headers、json数据中的{{xxx}}值
        url = self.replace_load(url)
        for key in kwargs.keys():
            if key in ["params", "data", "headers", "json"]:
                if not kwargs[key]:  # headers等如果是None不处理
                    continue
                kwargs[key] = self.replace_load(kwargs[key])
            if key == "data":
                # 处理中文编码问题，以bytes的方式传输数据
                kwargs[key] = json.dumps(kwargs[key],
                                         ensure_ascii=False).encode("utf8")
        if kwargs.get("files"):
            # 处理文件上传，使用with避免文件对象没有关闭
            for key in kwargs["files"].keys():
                with open(kwargs["files"][key], "rb") as f:
                    kwargs["files"][key] = f
                    log_util.write_log(">>>>>>>>>> 开始请求 >>>>>>>>>>>")
                    res = self.s.request(method=method, url=url, **kwargs)
        else:
            log_util.write_log(">>>>>>>>>> 请求开始 >>>>>>>>>>>")
            res = self.s.request(method=method, url=url, **kwargs)
        # 记录请求信息 log
        log_util.write_log("用例名称:" + case_name)
        log_util.write_log("url:" + url)
        log_util.write_log(f"method: {method}")
        if kwargs.get("data"):
            kwargs["data"] = kwargs["data"].decode()
        log_util.write_log(f"其它请求参数: {kwargs}")
        log_util.write_log(">>>>>>>>>> 请求结束 >>>>>>>>>>>")

        return res


if __name__ == "__main__":
    pass
