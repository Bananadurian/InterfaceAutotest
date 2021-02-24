# author:qinjinfeng
# date:2020-11-05

from appium import webdriver
import time
import json


def get_desired_caps():
    # TODO 文件存在的时候抛出异常
    with open('caps_config.json') as f:
        desired_caps = json.load(f)
    return desired_caps


class Utils(object):
    def __init__(self, desired_caps):
        # TODO 文件不存在的时候抛出异常
        with open('button_list.json', encoding='utf8') as f:
            self.all_button_dic = json.load(f)
        # TODO 连接失败的时候抛出异常
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub',
                                       desired_caps)
        self.driver.implicitly_wait(8)

    def start(self, case_list):
        button_element_dic = {}
        for case in case_list:
            if case['case_page'] in self.button_dic:
                button_dic = self.all_button_dic[case['case_page']]
            else:
                print("没有 {} 页面的button数据!!!".format(case['case_page']))
                continue
            for step in case.get('case_steps').values():
                if step in button_element_dic:
                    time.sleep(0.5)
                    button_element_dic[step].click()
                    # print("使用暂存信息")
                else:
                    # TODO 元素查找超时或失败的时候抛出异常
                    button_emlment = self.driver.find_element_by_xpath(step)
                    button_emlment.click()
                    button_element_dic[step] = button_emlment
                    # print('暂存信息')
        print('用例执行结束！！！')
        # print(button_element_dic)


if __name__ == '__main__':
    # TODO 文件存在的时候抛出异常
    with open('test_case.json', encoding='utf8') as f:
        case_list = json.load(f)

    demo = Utils(get_desired_caps())
    demo.start(case_list)
