# -*- coding: utf-8 -*-
import datetime
import time

from odoo import models, fields, api

from .test_token import get_department_user, get_attendance_list, get_users_name, get_department

# 员工档案、考勤异常、考勤明细、补卡申请、系统设置（信息同步、权限设置）
STATE_SELECTION = [
    ('draft', '草稿'),
    ('confirm', '待审批'),
    ('reject', '审批不通过'),
    ('complete', '审批通过')
]


class File(models.Model):
    _name = 'check.file'
    _description = '员工档案表'

    job_id = fields.Char('员工id')
    name = fields.Char('姓名')
    department = fields.Char('部门')
    number = fields.Integer('补卡次数', default=1)

    @api.multi
    def button_create_user(self):
        user_id_list, user_name_list, user_dept_list = get_department_user()
        id_name_dept = user_id_list + user_name_list + user_dept_list
        i = 0
        for num in user_id_list:
            if num:
                user_id = id_name_dept[i]
                user_name = id_name_dept[i + len(user_id_list)]
                user_dept = id_name_dept[i + 2 * len(user_id_list)]
                user_record = self.env["check.file"].search(
                    [('job_id', '=', user_id), ('name', '=', user_name), ('department', '=', user_dept)])
                if user_record:
                    print()
                else:
                    self.env['check.file'].create({'job_id': user_id, 'name': user_name, 'department': user_dept})
                i += 1
            else:
                print()


class Unusual(models.Model):
    _name = 'check.unusual'
    _description = '考勤异常表'

    job_id = fields.Char('员工id')
    name = fields.Char('姓名')
    ex_time = fields.Char('异常时间')
    replaced_card = fields.Boolean('已补卡')

    @api.multi
    def button_create_unusual(self):
        user_list = get_attendance_list()
        users_id, users_name = get_users_name()
        i = 0
        for user in user_list:
            if user and user_list[i]['timeResult'] != 'Normal':
                user_id = user_list[i]['userId']
                timestamp1 = user_list[i]['workDate']
                user_time1_str = str(timestamp1)
                time1_stamp = int(user_time1_str[0:10])
                datetime_struct1 = datetime.datetime.fromtimestamp(time1_stamp)
                datetime_obj1 = (datetime_struct1 + datetime.timedelta(hours=8))
                ex_work_day = datetime_obj1.strftime('%Y-%m-%d')
                j = 0
                for user_list_id in users_id:
                    if user_id == user_list_id:
                        user_name = users_name[j]
                    else:
                        j += 1
                user_record = self.env["check.unusual"].search(
                    [('job_id', '=', user_id), ('name', '=', user_name), ('ex_time', '=', ex_work_day)])
                if user_record:
                    print()
                else:
                    self.env['check.unusual'].create(
                        {'job_id': user_id, 'name': user_name, 'ex_time': ex_work_day})
                i += 1


class Detail(models.Model):
    _name = 'check.detail'
    _description = '考勤明细表'

    job_id = fields.Char('员工id')
    name = fields.Char('姓名')
    first_time = fields.Char('打卡时间一')
    second_time = fields.Char('打卡时间二')

    @api.multi
    def button_create_attend(self):
        user_list = get_attendance_list()
        users_id, users_name = get_users_name()
        i = 0
        for user in user_list:
            if user:
                user_id = user_list[i]['userId']
                timestamp1 = user_list[i]['userCheckTime']
                user_time1_str = str(timestamp1)
                time1_stamp = int(user_time1_str[0:10])
                datetime_struct1 = datetime.datetime.fromtimestamp(time1_stamp)
                datetime_obj1 = (datetime_struct1 + datetime.timedelta(hours=8))
                time1 = datetime_obj1.strftime('%Y-%m-%d %H:%M:%S')
                time2 = ''
                j = 0
                for user_list_id in users_id:
                    if user_id == user_list_id:
                        user_name = users_name[j]
                    else:
                        j += 1
                if i < len(user_list) - 1 and user_list[i + 1]['checkType'] == 'OffDuty':
                    timestamp2 = user_list[i]['userCheckTime']
                    user_time2_str = str(timestamp2)
                    time2_stamp = int(user_time2_str[0:10])
                    datetime2_struct = datetime.datetime.fromtimestamp(time2_stamp)
                    datetime2_obj = (datetime2_struct + datetime.timedelta(hours=8))
                    time2 = datetime2_obj.strftime('%Y-%m-%d %H:%M:%S')
                user_record = self.env["check.detail"].search(
                    [('job_id', '=', user_id), ('name', '=', user_name), ('first_time', '=', time1),
                     ('second_time', '=', time2)])
                if user_record:
                    print()
                else:
                    self.env['check.detail'].create(
                        {'job_id': user_id, 'name': user_name, 'first_time': time1, 'second_time': time2})
                i += 1


class Apply(models.Model):
    _name = 'check.apply'
    _description = '补卡申请表'

    job_id = fields.Char('员工id', )
    name = fields.Char('姓名', default=lambda self: self.env.user)
    ex_time = fields.Datetime('异常时间')
    ex_reason = fields.Char('异常原因')
    state = fields.Selection(STATE_SELECTION, default='draft', string='状态', readonly=True, copy=False,
                             track_visibility='onchange')

    def button_submit(self):
        return self.write({'state': 'confirm'})

    def button_pass(self):
        return self.write({'state': 'complete'})

    def button_fail(self):
        return self.write({'state': 'reject'})


class Department(models.Model):
    _name = 'check.department'
    _description = '部门信息表'

    name = fields.Char('部门名称')

    @api.multi
    def button_create_department(self):
        dept_ids, dept_names = get_department()
        for dept_name in dept_names:
            if dept_name:
                self.env['check.department'].create({'name': dept_name})


class Syn(models.Model):
    _name = 'check.syn'
    _description = '信息同步表'


class User(models.Model):
    _inherit = "res.users"

    test_name = fields.Char(string='姓名', required=True)
    test_department = fields.Char(string='部门')

    @api.multi
    def button_create_user_dept(self):
        id_list, name_list, dept_name_list = get_department_user()
        i = 0
        for user_name in name_list:
            if user_name:
                test_user_name = user_name
                test_dept = dept_name_list[i]
                user_record = self.env["res.users"].search(
                    [('test_name', '=', test_user_name), ('test_department', '=', test_dept)])
                if user_record:
                    print()
                else:
                    self.env['res.users'].create(
                        {'test_name': test_user_name, 'test_department': test_dept})
                i += 1
