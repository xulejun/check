import urllib.request

import json

import requests

access_token = ''


def get_token():
    '''获取钉钉的token
    :return: 钉钉token'''

    appkey = 'dingeqvytro5lbiriu8o'
    appsecret = 'hnTUfB-kQnwO3mXFtQnZJPGs5Ph4ZFsUAgwhiFVxQVbAaJLlc8WsZdo_F8GxJGbG'
    global access_token
    headers = {
        'Content-Type': 'application/json',
    }
    url = 'https://oapi.dingtalk.com/gettoken?appkey=%s&appsecret=%s' % (appkey, appsecret)
    req = requests.get(url, headers=headers)
    result = json.loads(req.text)
    access_token = result.get('access_token')


def get_department():
    dept_ids = []
    dept_names = []
    headers = {
        'Content-Type': 'application/json',
    }
    url = 'https://oapi.dingtalk.com/department/list?access_token=%s' % (access_token)
    req = requests.get(url, headers=headers)
    result = json.loads(req.text)
    # result_json = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)  # 以json的格式输出
    dept_name_list = result.get('department')
    i = 0
    for dept_name in dept_name_list:
        if dept_name:
            dept_ids.append(dept_name_list[i]['id'])
            dept_names.append(dept_name_list[i]['name'])
            i += 1
        else:
            print()
    return dept_ids, dept_names


def get_department_user():
    headers = {
        'Content-Type': 'application/json',
    }
    department_id_list, department_name_list = get_department()
    id_list = []
    name_list = []
    dept_id_name_list = dict(zip(department_id_list, department_name_list))
    dept_name_list = []
    for department in department_id_list:
        department_id = department
        url = 'https://oapi.dingtalk.com/user/listbypage?access_token=%s&department_id=%s&offset=0&size=100' % (
            access_token, department_id)
        req = requests.get(url, headers=headers)
        list1 = json.loads(req.text)
        userlist = list1.get('userlist')
        i = 0
        for user in userlist:
            for key in dept_id_name_list:
                if department_id == key:
                    dept_name_list.append(dept_id_name_list[key])
            if user:
                id_list.append(userlist[i]['jobnumber'])
                name_list.append(userlist[i]['name'])
                i += 1
            else:
                print()
    return id_list, name_list, dept_name_list


def get_users_id():
    dept_ids, dept_names = get_department()
    headers = {
        'Content-Type': 'application/json',
    }
    user_ids = []
    for dept_id in dept_ids:
        url = 'https://oapi.dingtalk.com/user/getDeptMember?access_token=%s&deptId=%s' % (access_token, dept_id)
        req = requests.get(url, headers=headers)
        list1 = json.loads(req.text)
        user_ids += list1['userIds']
    return user_ids


def get_attendance_list():
    user_ids = get_users_id()
    headers = {
        "userIds": user_ids,
        "checkDateFrom": "2019-12-20 00:00:00",
        "checkDateTo": "2019-12-21 00:00:00",
        "isI18n": "false"
    }
    url = 'https://oapi.dingtalk.com/attendance/listRecord?access_token=%s' % (access_token)
    req = requests.post(url, json.dumps(headers))
    result = json.loads(req.text)
    result_json = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)  # 以json的格式输出
    print(result_json)


get_token()
get_department()
get_department_user()
get_users_id()
get_attendance_list()