import pytest
import os


if __name__ == "__main__":
    pytest.main()
    # 生成本地allure报告
    os.system("allure generate ./report/temp -o ./report/allure_report -c")
    # 打开本地报告
    os.system("allure open ./report/allure_report")
