from common.request_util import RequestUtil
from common import yaml_util
from common import parameters_util
from common.log_util import error_log, write_log
from common.allure_report_util import report_format
import pytest
import allure


@pytest.fixture(scope="module", autouse=False)
def get_access_token():
    # 前置步骤，用于获取token信息，目前没有使用
    url_path = "/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": "wxd3bf30272b1def4f",
        "secret": "3df1dde2526a65de86c5e18db3f2d421"
    }
    res = RequestUtil("WeChat").send_request("get",
                                             url_path=url_path,
                                             params=params)
    yaml_util.write_extract_file({"access_token": res.json()["access_token"]})
    print(">>>>>>>>: 获取token成功")


class TestWeChatLogin:
    @pytest.mark.run(order=1)
    @pytest.mark.parametrize(
        "case_data",
        parameters_util.format_all_case_data(__file__))
    def test_get_tag(self, case_data):
        report_format(case_data)  # 处理报告信息

        try:
            res, assert_flag, assert_msg = RequestUtil().analysis_yaml(
                case_data)
        except Exception as e:
            error_log(e)

        if isinstance(res, str):
            assert False, res
        print(res.status_code)
        print(">>>>>:请求url")
        print(res.url)
        print(">>>>>:请求body")
        print(res.request.body)
        print(">>>>>: 响应数据")
        print(res.json())
        allure.attach(res.text, "响应结果", allure.attachment_type.JSON)

        if assert_msg:
            write_log(assert_msg, "error")

        assert assert_flag == 0, assert_msg