#!/usr/bin/python3
# -*- coding: utf-8 -*-
# import urllib3
import requests
import json
import os
from io import BytesIO
import time
import pytz
import datetime
import jenkins

user_name = {
    "zhuxunhua":"朱勋华",
    "liupeihong":"刘培宏",
    "wufeifei":"吴飞飞",
    "xierunan":"谢如楠",
    "yangkai":"杨凯",
    "yinzhiyua":"伊志远",
    "kuangxianxin":"旷先信",
    "xianxin.kuang":"旷先信",
    "Dandelion":"梁承鹏",
    "liangchengpeng":"梁承鹏"
}

path = "result.txt"
    
def check_status():
    fd = open(path, "r")
    line = fd.read()
    print("line:", line)
    
    fd.close()

    return line

def set_status():
    fd = open(path, "w+")
    fd.write("wait")
    
    fd.close()


def splice_data():
    #time.sleep(5)
    # 最后一次构建的URL
    last_build_url = "curl http://192.168.2.28:8080/job/vicenter_check/lastBuild/api/json --user liangchengpeng:liangchengpeng"
    job_url = "curl http://192.168.2.28:8080/job/vicenter_check/api/json --user liangchengpeng:liangchengpeng"

    # 模拟curl请求数据，返回的是JSON格式的数据
    last_build_data = os.popen('curl %s' % last_build_url).readlines()
    # print("last_build_data:", last_build_data)
    # 加载成JSON格式的数据
    last_build_data = json.loads(last_build_data[0])

    # 模拟curl请求数据，返回的是JSON格式的数据
    job_data = os.popen('curl %s' % job_url).readlines()
    # print("job_data:", job_data)
    # 加载成JSON格式的数据
    job_data = json.loads(job_data[0])

    # 拼接数据
    build_user_info = last_build_data["actions"][0]["causes"][0]["shortDescription"]
    # print("build_user_name:", build_user_name)
    list = build_user_info.split(" ")
    # print(list[len(list)-1])
    build_user_name = list[len(list)-1]
    build_user_name = switch_user_name(build_user_name)

    build_result = str(last_build_data["result"])
    build_time = get_time(last_build_data["timestamp"])
    build_number = str(last_build_data["number"])
    build_url = last_build_data["url"]
    build_duration = last_build_data["duration"] / 1000
    build_m, build_s = divmod(build_duration, 60)
    task_name = job_data["name"]

    build_m = "{:.0f}".format(build_m)
    build_s = "{:.0f}".format(build_s)
    # print(build_m, build_s)
    build_duration = build_m + "分" + build_s + "秒"

    build_branch = "dev"

    check_result = ""
    if get_compile_result_size() == True:
        check_result = "session测试通过"
    else:
        check_result = "session有语法错误"
    
    #head_info = "[ " + "<font color=\"warning\">" + task_name + "</font>" + " ]" + " 构建: " + build_result + "\n"
    head_info = "[ " + task_name +" ]" + " 构建: " + build_result + "\n"
    basic_data = [
        head_info,
        "> 构建用户: " + build_user_name + "\n",
        "> 构建分支: " + build_branch + "\n",
        "> 构建起始: " + build_time + "\n",
        "> 构建时长: " + build_duration + "\n",
        "> 构建次数: " + build_number + "\n",
        "> 详细信息: " + build_url + "\n",
        "> 构建结果: " + build_result + "\n",
        "> 测试结果: " + check_result,
    ]

    print_data = ''
    for cnt in range(len(basic_data)):
        print_data = print_data + basic_data[cnt]

    # print(print_data)

    return print_data

# 判断vicenter check的结果
def get_compile_result_size():
    file = "/script/check_vicenter/compile_result.txt"
    size = os.path.getsize(file)
    print("compile_result.txt size:", size)
    if size == 0:
        print("vicenter check success !!!")
        return True
    else:
        print("vicenter check fail !!!")
        return False

# 通过键值关系，由输入的gitlab使用名称转换成中文名
def switch_user_name(build_user_name):
    build_name = ""
    try:
        build_name = user_name[build_user_name]
    except Exception:
        build_name = build_user_name

    print("build_user_name:", build_name)
    return build_name

def wechatwork():
    # 测试组
    #webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=08cf8818-68fc-4c21-8255-13fd0073bdfe"
    # CI通知群
    webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=fa8c0bd1-2b65-483e-ab9b-9c30afb45bad"
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"}

    message ={
        "msgtype": "text",
        "text": {
            "content": splice_data()
        },
        "at": {
            "isAtAll": True
        }

    }
    message_json = json.dumps(message)
    info = requests.post(url=webhook,data=message_json,headers=header, verify=False)
    print(info.text)


#定义xml转json的函数
def xml_to_json(xmlstr):
    #parse是的xml解析器
    xmlparse = xmltodict.parse(xmlstr)
    #json库dumps()是将dict转化成json格式，loads()是将json转化成dict格式。
    #dumps()方法的ident=1，格式化json
    jsonstr = json.dumps(xmlparse,indent=1)

    print_data = json.loads(jsonstr)
    # print("print_data:", print_data)

    return print_data

# 把时间戳转换成时间（输入单位是毫秒）
def get_time(timestamp):
    # 把毫秒转换成秒
    value = int(timestamp)/1000
    tz = pytz.timezone('Asia/Shanghai')
    # 转换为上海时间
    time_local = pytz.datetime.datetime.fromtimestamp(value, tz)
    dt = time_local.strftime('%Y-%m-%d %H:%M:%S')
    #转换成localtime
    #time_local = time.localtime(value)
    #转换成新的时间格式(2016-05-05 20:28:54)
    #dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    print("dt:", dt)

    return dt

if __name__ == '__main__':
    cnt = 0
    while True:
        cnt = cnt + 1
        print("monitor heartbeat:", cnt)

        if check_status() == "over":
            # 等待五秒后执行
            time.sleep(5)
            
            # 执行Jenkins到企业微信这段的功能
            wechatwork()

            # 文件状态设置为wait
            set_status()


        # 休眠一秒钟
        time.sleep(2)