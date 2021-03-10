#!usr/bin/env python
# -*- coding:utf-8 -*-
""" PyCharm
@author: oGsLP
@file: main.py
@time: 2020/12/24 12:40
@function: automatically choose class for nju masters
"""

import time
import requests
import yaml

from util.des_encrypt import strEncSimple
from util.number_identifier import NumberIdentifier

WEU = ""
cookie = "_WEU=%s; _ga=GA1.3.624467535.1605355636; route=cd43b6d3bb4369a40cab748104f44526; JSESSIONID=F8ohqfxR9ePxSJIEp08Kc4G71JI_sXMvQJ1sm7R_CCvuyqHgxyjk!358279823; XK_TOKEN=ebca04d2-22a5-407a-944e-a4122a530dc0"

root_url = "https://yjsxk.nju.edu.cn/yjsxkapp/sys/xsxkapp/"

index_url = root_url + "login/4/vcode.do?timestamp=%d"
image_url = root_url + "login/vcode/image.do?vtoken=%s"

login_url = root_url + "login/check/login.do?timestrap=%d"

list_url = root_url + "xsxkHome/loadPublicInfo_course.do"
courses_url = root_url + "xsxkCourse/loadFanCourseInfo.do?_=%d"
choose_url = root_url + "xsxkCourse/choiceCourse.do?_=%d"

headers = {
    "Accept": 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Content-Length': '86',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': "",
    'Host': 'yjsxk.nju.edu.cn',
    'Origin': 'https://yjsxk.nju.edu.cn',
    'Referer': 'https://yjsxk.nju.edu.cn/yjsxkapp/sys/xsxkapp/course_nju.html',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47',
    'X-Requested-With': 'XMLHttpRequest'
}

refresh_headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Cookie': "",
    'Host': 'yjsxk.nju.edu.cn',
    'Referer': 'https://yjsxk.nju.edu.cn/yjsxkapp/sys/xsxkapp/course_nju.html',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47'
}

courses = [
    # "20202-032-085212C01-1604969834471",
    # "20202-032-085212C02-1604969833474",
    # "20202-032-085212D02-1604969834149",
    # "20202-032-085212D14-1604969833901",
    # "20202-032-085212D17-1604969834440",
    # "20202-032-085212D13-1604969833733"
]

names = [
    # "人机交互",
    # "敏捷开发",
    # "分布式系统",
    # "大数据",
    # "软件过程改进",
    # "体系结构"
]

name = ""
passwd = ""

pic = 'number.jpeg'

csrftoken = ""
vtoken = ""
identifier = None


def configure_identifier():
    with open('./configuration.yaml', 'r', encoding='utf-8') as f:
        file_content = f.read()
    configuration = yaml.load(file_content, yaml.FullLoader)

    # configure number & passwd by the way
    global name, passwd
    name = configuration["yjsxk"]["number"]
    passwd = configuration["yjsxk"]["password"]

    return NumberIdentifier(configuration["chaojiying"]["username"], configuration["chaojiying"]["password"],
                            configuration["chaojiying"]["softid"])


def get_vtoken():
    res = requests.get(index_url % get_timestamp())
    data = res.json()

    global vtoken
    if int(data["code"]) == 1:
        vtoken = data["data"]["token"]

    res.close()


def get_image():
    res = requests.get(image_url % vtoken)
    with open(pic, 'wb') as f:
        f.write(res.content)


def login():
    global identifier, WEU, headers, refresh_headers
    identifier = configure_identifier()
    get_vtoken()
    get_image()
    verify_code = identifier.post_pic(open(pic, 'rb').read(), 1902)["pic_str"]
    code = 0
    res = None
    while code != 1:
        res = requests.post(login_url % get_timestamp(), data={
            "loginName": name,
            "loginPwd": strEncSimple(passwd),
            "verifyCode": verify_code,
            "vtoken": vtoken
        })
        data = res.json()
        print(data)
        code = int(data["code"])

    for c in res.cookies:
        if c.name == "_WEU":
            WEU = c.value
            break
    headers["Cookie"] = cookie % WEU
    refresh_headers["Cookie"] = cookie % WEU
    res.close()


def refresh_csrftoken():
    res = requests.get(list_url, headers=refresh_headers)
    data = res.json()
    global csrftoken
    csrftoken = data["csrfToken"]
    res.close()


def load_courses():
    res = requests.post(courses_url % get_timestamp(), data={
        "pageIndex": 1,
        "pageSize": 20
    }, headers=headers)

    data = (res.json())["datas"]

    for item in data:
        names.append(f"{item['KCDM']} - {item['KCMC']} ({item['BJMC']})")
        courses.append(item["BJDM"])


def crawl_course(i):
    res = requests.post(
        choose_url % get_timestamp(), data={
            "bjdm": courses[i],
            "lx": 2,
            "csrfToken": csrftoken
        }, headers=headers)

    data = res.json()

    print("  [%s]: %s" % (names[i], data["msg"]))

    res.close()

    return int(data['code']) == 1


def get_timestamp():
    return int(time.time() * 1000)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    count = 0
    start = time.time()
    login()
    refresh_csrftoken()
    load_courses()
    while True:
        if time.time() - start > 2 * 60 * 60:
            start = time.time()
            login()
            refresh_csrftoken()
        print(
            "(%s) <csrfToken: %s> COUNT:%d" % (
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), csrftoken, count + 1))
        for i in range(len(courses)):
            bl = crawl_course(i)
            if bl:
                del courses[i]
                del names[i]
                break
            # time.sleep(0.05)
        time.sleep(0.1)
        count = count + 1
        if count > 1:
            refresh_csrftoken()
            count = 0
