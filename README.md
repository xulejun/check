# odoo同步钉钉考勤信息

功能要求：
1、 建立员工档案表、考勤异常表、考勤明细表。

2、 从钉钉同步在职员工基本信息，每半小时一次，可手动同步。

3、 从钉钉同步员工考勤数据，每半小时一次，可手动同步。

4、 考勤明细表记录所有考勤信息，异常表只记录考勤异常的记录

5、 补卡申请表单状态：草稿、提交申请、审批中、修改中（驳回状态）、审批通过，按钮根据状态显示。

6、 员工每个月只有一次补卡机会，当补卡次数为0时，可以创建补卡申请表单。补卡申请表状态为通过时，考勤异常表显示该时间段已补卡，补卡次数减少。

7、菜单规划：员工档案、考勤异常、考勤明细、补卡申请、系统设置（信息同步、权限设置），根据角色可见。

8、权限设置：
管理员：拥有全部权限，可进行同步操作
部门经理：拥有自己部门的考勤异常表、考勤明细表、员工档案表和审批自己部门员工补卡申请表的权限
协调人：拥有审批补卡申请表的权限
普通用户：可查看个人考勤明细，考勤异常表，可提交补卡申请表，审批状态为审批中，则不可修改表单（按月）
