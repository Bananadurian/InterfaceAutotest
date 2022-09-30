import allure


def report_format(case_data: dict) -> None:
    """格式化报告信息

    Args:
        case_data (dict): 用例信息
    """
    if case_data.get("report_info"):
        report_info = case_data["report_info"]
        # 项目名称
        if report_info.get("epic"):  # 取到值的时候执行，空字符串的时候也不会执行
            allure.dynamic.label("epic", report_info["epic"])
        # 模块名称
        if report_info.get("feature"):
            allure.dynamic.feature(report_info["feature"])
        # 分组信息
        if report_info.get("story"):
            allure.dynamic.story(report_info["story"])
        # 标签
        if report_info.get("tags"):
            for tag in report_info["tags"]:
                allure.dynamic.tag(tag)
    # 用例名称
    allure.dynamic.title(case_data["name"])
    # 用例描述信息
    allure.dynamic.description(case_data["des"])