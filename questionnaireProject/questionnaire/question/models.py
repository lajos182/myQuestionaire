from datetime import date

from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# *****************************客户***********************************
class Customer(models.Model):
    # 客户信息
    name = models.CharField(default='名称', max_length=32, help_text='客户名称')
    email = models.CharField(default='', max_length=64, null=True, blank=True, help_text='邮箱')
    company = models.CharField(default='', max_length=32, null=True, blank=True, help_text='公司名称')
    address = models.CharField(default='', max_length=256, null=True, blank=True, help_text='地址')
    mobile = models.CharField(default='', max_length=16, null=True, blank=True, help_text='手机号码')
    phone = models.CharField(default='', max_length=16, null=True, blank=True, help_text='座机')
    qq = models.CharField(default='', max_length=16, null=True, blank=True, help_text='QQ')
    wechat = models.CharField(default='', max_length=64, null=True, blank=True, help_text='微信号')
    web = models.CharField(default='', max_length=64, null=True, blank=True, help_text='网站地址')
    industry = models.CharField(default='', max_length=32, null=True, blank=True, help_text='行业')
    description = models.TextField(default='', null=True, blank=True, help_text='公司简介')


class Questionnaire(models.Model):
    # 问卷
    customer = models.ForeignKey('Customer', help_text='客户信息')
    title = models.CharField(default='标题', max_length=64, help_text='标题')
    create_date = models.DateTimeField(help_text='创建时间')
    deadline = models.DateTimeField(help_text='截止时间')
    quantity = models.IntegerField(default=1, help_text='发布数量')
    free_count = models.IntegerField(default=1, help_text='可用问卷数量')
    state = models.IntegerField(default=0, help_text='状态, 0→草稿,1→待审核,2→审核失败,3→身体通过,4→已发布')
    type = models.CharField(default='', max_length=64, null=True, blank=True, help_text='问卷类型')


class Question(models.Model):
    # 题目
    # on_delete=models.CASCADE 级联删除，关联的数据都会被删除
    questionnaire = models.ForeignKey('Questionnaire', help_text='问卷', on_delete=models.CASCADE)
    title = models.CharField(max_length=128, help_text='题纲')
    index = models.IntegerField(default=0, help_text='题号', db_index=True)
    category_choices = [('radio', '单选'), ('select', '多选'),]
    category = models.CharField(choices=category_choices, default='radio', max_length=16, help_text='是否多选')
    required_question = models.BooleanField(default=1, help_text='是否必答, 0→未答题,1→必答题')

class QuestionItem(models.Model):
    # 题目选项
    question = models.ForeignKey('Question', help_text='题目', on_delete=models.CASCADE)
    content = models.CharField(max_length=32, help_text='选项内容')
    order_number = models.IntegerField(default=0, help_text='序号')

class Wallet(models.Model):
    # 客户钱包
    customer = models.OneToOneField('Customer', help_text='客户')
    balance = models.FloatField(default=0, help_text='余额')

class WalletOutflow(models.Model):
    # 消费记录
    wallet = models.ForeignKey('Wallet', help_text='钱包')
    create_date = models.DateTimeField(auto_now=True, help_text='交易时间')
    amount = models.FloatField(default=0, help_text='发生金额')
    consume_state = models.BooleanField(default=1, help_text='是否支付, 0→待支付,1→已支付')
    serial_number = models.CharField(max_length=128, help_text='消费流水号')

class WalletInflow(models.Model):
    # 充值记录
    wallet = models.ForeignKey('Wallet', help_text='钱包')
    create_date = models.DateTimeField(auto_now=True, help_text='交易时间')
    amount = models.FloatField(default=0, help_text='发生金额')
    consume_state = models.BooleanField(default=1, help_text='是否支付, 0→待支付,1→已支付')
    recharge_type = models.CharField(max_length=32, choices=[('alipay', '支付宝'), ('wechat', '微信')], help_text="支付方式")
    recharge_id = models.CharField(max_length=128, help_text='充值记录')
    serial_number = models.CharField(max_length=128, help_text='消费流水号')

# *****************************管理员***********************************
class Administrator(models.Model):
    name = models.CharField(default='名称', max_length=32, help_text='用户名')
    password = models.CharField(max_length=16, help_text='管理员密码')

class QuestionnaireCheck(models.Model):
    questionnaire = models.ForeignKey('Questionnaire', help_text="问卷", on_delete=models.CASCADE)
    # administrator = models.ForeignKey('Administrator', help_text='管理员')
    create_date = models.DateTimeField(auto_now=True, help_text="审核时间")
    comment = models.TextField(help_text="审核批注")

# *****************************普通用户***********************************
class UserInfo(models.Model):
    # 用户信息
    user = models.OneToOneField(User)
    name = models.CharField(default='姓名', max_length=32, help_text='姓名')
    age = models.IntegerField(default=1, help_text='年龄')
    sex = models.BooleanField(default=1, help_text='性别, 0→女, 1→男')
    phone = models.CharField(default='', max_length=16, blank=True, null=True, help_text='手机号码')
    email = models.CharField(default='', max_length=64, blank=True, null=True, help_text='邮箱')
    address = models.CharField(default='', max_length=256, blank=True, null=True, help_text='地址')
    birthday = models.DateTimeField(default=date(2018, 1, 1), null=True, help_text='出生日期')
    qq = models.CharField(default='', max_length=16, blank=True, null=True, help_text='QQ')
    wechat = models.CharField(default='', max_length=64, blank=True, null=True, help_text='微信号')
    job = models.CharField(default='', max_length=32, blank=True, null=True, help_text='职业')
    hobby = models.CharField(default='', max_length=64, blank=True, null=True, help_text='兴趣爱好')
    salary = models.CharField(default='', max_length=32, blank=True, null=True, help_text='收入水平')


class Point(models.Model):
    # 用户积分
    userinfo = models.OneToOneField('UserInfo', help_text='用户信息')
    balance = models.IntegerField(default=0, help_text='余额')

class GetPoint(models.Model):
    # 获取积分
    userinfo = models.OneToOneField('UserInfo', help_text='用户信息')
    amount = models.IntegerField(default=0, help_text='积分值')
    create_date = models.DateTimeField(auto_now=True, help_text='积分获取时间')
    reason = models.CharField(default='', max_length=64, help_text='获取原因')

class UsePoint(models.Model):
    # 积分使用记录
    userinfo = models.OneToOneField('UserInfo', help_text='用户信息')
    amount = models.IntegerField(default=0, help_text='积分值')
    create_date = models.DateTimeField(auto_now=True, help_text='积分获取时间')
    reason = models.CharField(default='', max_length=64, help_text='积分使用原因')

class Answer(models.Model):
    # 参与问卷
    userinfo = models.ForeignKey('UserInfo', null=True, help_text='用户信息')
    questionnaire = models.ForeignKey('Questionnaire', help_text="问卷")
    create_date = models.DateTimeField(auto_now=True, help_text='参与问卷日期')
    is_done = models.BooleanField(default=False, help_text='是否已经完成')

class AnswerItem(models.Model):
    # 用户回答题目
    userinfo = models.ForeignKey('UserInfo', null=True, help_text='用户信息')
    item = models.ForeignKey('QuestionItem', help_text='选项')