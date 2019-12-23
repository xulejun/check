# -*- coding: utf-8 -*-

from odoo import models, fields, api

from .test_token import get_department_user, get_attendance_list, get_users_name, get_unusual

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
    ex_time = fields.Datetime('异常时间')
    replaced_card = fields.Boolean('已补卡')

    @api.multi
    def button_unusual_time(self):
        user_id_list, user_ex_time = get_unusual()
        users_name_list = get_users_name()
        id__name_time = user_id_list + users_name_list + user_ex_time
        i = 0
        for num in user_id_list:
            if num:
                user_id = id__name_time[i]
                user_name = id__name_time[i + len(user_id_list)]
                user_time = id__name_time[i + 2 * len(user_id_list)]
                self.env['check.detail'].create(
                    {'job_id': user_id, 'name': user_name, 'ex_time': user_time})
                i += 1
            else:
                print()


class Detail(models.Model):
    _name = 'check.detail'
    _description = '考勤明细表'

    job_id = fields.Char('员工id')
    name = fields.Char('姓名')
    first_time = fields.Char('打卡时间一')
    second_time = fields.Char('打卡时间二')

    @api.multi
    def button_create_attend(self):
        user_id_list, user_time1_list, user_time2_list = get_attendance_list()
        users_name_list = get_users_name()
        id__name_time1_time2 = user_id_list + users_name_list + user_time1_list + user_time2_list
        i = 0
        for num in user_id_list:
            if num:
                user_id = id__name_time1_time2[i]
                user_name = id__name_time1_time2[i + len(user_id_list)]
                user_time1 = id__name_time1_time2[i + 2 * len(user_id_list)]
                user_time2 = id__name_time1_time2[i + 3 * len(user_id_list)]
                self.env['check.detail'].create(
                    {'job_id': user_id, 'name': user_name, 'first_time': user_time1, 'second_time': user_time2})
                i += 1
            else:
                print()


class Apply(models.Model):
    _name = 'check.apply'
    _description = '补卡申请表'

    job_id = fields.Char('员工id')
    name = fields.Char('姓名')
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


class Syn(models.Model):
    _name = 'check.syn'
    _description = '信息同步表'


class Permission(models.Model):
    _name = 'check.permission'
    _description = '权限设置'


class User(models.Model):
    _inherit = "res.users"

    name = fields.Char(string='姓名', required=True)
    department = fields.Many2one('check.department', string='部门')
