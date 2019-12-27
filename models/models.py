# -*- coding: utf-8 -*-
import datetime
import time

from odoo import models, fields, api, exceptions

from .test_token import get_department_user, get_attendance_list, get_users_name, get_department, get_parent_ids

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


class Unusual(models.Model):
    _name = 'check.unusual'
    _description = '考勤异常表'

    job_id = fields.Char('员工id')
    department = fields.Char('部门')
    name = fields.Char(string='异常时间')
    ex_state = fields.Char('异常状态')
    ex_time = fields.Char(string='姓名')
    replaced_card = fields.Boolean('已补卡')


class Detail(models.Model):
    _name = 'check.detail'
    _description = '考勤明细表'

    department = fields.Char('部门')
    job_id = fields.Char('员工id')
    name = fields.Char('姓名')
    first_time = fields.Char('打卡时间一')
    second_time = fields.Char('打卡时间二')


class Apply(models.Model):
    _name = 'check.apply'
    _description = '补卡申请表'

    job_id = fields.Char(string='员工id', default=lambda self: self.env.user.test_id, readonly=True)
    name = fields.Char(string='姓名', default=lambda self: self.env.user.test_name, readonly=True)
    department = fields.Char(string='部门', default=lambda self: self.env.user.test_department, readonly=True)
    ex_time = fields.Many2one('check.unusual', string='异常时间', states={'draft': [('readonly', False)]}, readonly=True,
                              required=True)
    ex_time1 = fields.Char(related='ex_time.name')
    ex_reason = fields.Char(string='异常原因', states={'draft': [('readonly', False)]}, readonly=True)
    state = fields.Selection(STATE_SELECTION, default='draft', string='状态', readonly=True, copy=False,
                             track_visibility='onchange')

    def button_submit(self):
        return self.write({'state': 'confirm'})

    def button_pass(self):
        file_rec = self.env['check.file'].search([])
        unusual_rec = self.env['check.unusual'].search([])
        for i in file_rec:
            # if self.job_id != i.job_id:
            #     continue
            if self.job_id == i.job_id and i.number > 0:
                for j in unusual_rec:
                    if self.job_id == j.job_id and self.name == j.ex_time and self.ex_time1 == j.name:
                        j.write({'replaced_card': True})
                        i.write({'number': 0})
                        self.write({'state': 'complete'})
                    # else:
                    #     raise exceptions.ValidationError("请核对用户补卡信息表")
            # else:
            #     raise exceptions.ValidationError("该用户补卡次数不足")

    def button_fail(self):
        return self.write({'state': 'reject'})


class Department(models.Model):
    _name = 'check.department'
    _description = '部门信息表'

    department_id = fields.Char('部门id')
    department_name = fields.Char('部门')


class Syn(models.Model):
    _name = 'check.syn'
    _description = '信息同步表'

    @api.multi
    def button_create_num(self):
        self.env['check.file'].write({'number': 1})

    @api.multi
    def button_create_file(self):
        # 权限用户
        user_id_list, user_name_list, user_dept_list = get_department_user()
        id_name_dept = user_id_list + user_name_list + user_dept_list
        i = 0
        for num in user_id_list:
            if num:
                user_id = id_name_dept[i]
                user_name = id_name_dept[i + len(user_id_list)]
                user_dept = id_name_dept[i + 2 * len(user_id_list)]
                user_record = self.env["res.users"].search([('login', '=', user_name), ('test_id', '=', user_id)])
                if user_record:
                    print()
                else:
                    partner_record = self.env["res.partner"].search([('name', '=', user_name)])
                    if partner_record:
                        pass
                    else:
                        partner_record = self.env["res.partner"].create({"name": user_name, "company_id": 1})
                    self.env['res.users'].create(
                        {'login': user_name, 'name': user_name, 'test_id': user_id, 'test_name': user_name,
                         'test_department': user_dept, "company_id": 1, "partner_id": partner_record.id,
                         "password": "123"})
                i += 1
            else:
                print()
        # 员工档案同步
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
        # 考勤明细方法
        user_list = get_attendance_list()
        users_id, users_name, user_dept_list = get_department_user()
        i = 0
        for user in user_list:
            if user_list[i]['checkType'] == 'OnDuty':
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
                    user_dept = user_dept_list[j]
                else:
                    j += 1
            if i < len(user_list) - 1 and user_list[i + 1]['checkType'] == 'OffDuty':
                timestamp2 = user_list[i + 1]['userCheckTime']
                user_time2_str = str(timestamp2)
                time2_stamp = int(user_time2_str[0:10])
                datetime2_struct = datetime.datetime.fromtimestamp(time2_stamp)
                datetime2_obj = (datetime2_struct + datetime.timedelta(hours=8))
                time2 = datetime2_obj.strftime('%Y-%m-%d %H:%M:%S')
            user_record = self.env["check.detail"].search(
                [('job_id', '=', user_id), ('name', '=', user_name), ('department', '=', user_dept),
                 ('first_time', '=', time1),
                 ('second_time', '=', time2)])
            if user_record:
                print()
            else:
                self.env['check.detail'].create(
                    {'job_id': user_id, 'name': user_name, 'department': user_dept, 'first_time': time1,
                     'second_time': time2})
            i += 1
        # 考勤异常获取方法
        user_list = get_attendance_list()
        users_id, users_name, user_dept_list = get_department_user()
        for user in user_list:
            if user['timeResult'] != 'Normal':
                user_id = user['userId']
                time_result = user['timeResult']
                timestamp1 = user['userCheckTime']
                user_time1_str = str(timestamp1)
                time1_stamp = int(user_time1_str[0:10])
                datetime_struct1 = datetime.datetime.fromtimestamp(time1_stamp)
                datetime_obj1 = (datetime_struct1 + datetime.timedelta(hours=8))
                time1 = datetime_obj1.strftime('%Y-%m-%d %H:%M:%S')
                j = 0
                for user_list_id in users_id:
                    if user_id == user_list_id:
                        user_name = users_name[j]
                        user_dept = user_dept_list[j]
                    else:
                        j += 1
                user_record = self.env["check.unusual"].search(
                    [('job_id', '=', user_id), ('department', '=', user_dept), ('ex_time', '=', user_name),
                     ('name', '=', time1)])
                if user_record:
                    print()
                else:
                    self.env['check.unusual'].create(
                        {'job_id': user_id, 'department': user_dept, 'ex_time': user_name, 'name': time1,
                         'ex_state': time_result})
        # 部门信息同步
        dept_ids, dept_names = get_department()
        parent_list = get_parent_ids()
        i = 0
        for dept_id in dept_ids:
            get_parent_id = parent_list[i]['parentIds']
            get_dept_name = dept_names[i]
            user_record = self.env["check.department"].search(
                [('department_id', '=', get_parent_id), ('department_name', '=', get_dept_name)])
            if user_record:
                print()
            else:
                self.env['check.department'].create({'department_id': get_parent_id, 'department_name': get_dept_name})
            i += 1


class User(models.Model):
    _inherit = "res.users"

    test_id = fields.Char(string='员工id')
    test_name = fields.Char(string='姓名')
    test_department = fields.Char(string='部门')
