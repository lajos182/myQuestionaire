import random
import json

from django.conf.urls import url
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from api.utils import *
from question.models import *

class Rest(object):
    def __init__(self, name=None):
        self.name = name or self.__class__.__name__.lower()
    # 定义一个方法用于绑定到url中
    @csrf_exempt  # 跨站请求伪造保护
    def enter(self, request, *args, **kwargs):
        # 去除客户端请求方法
        method = request.method
        # 根据请求方法执行响应的处理函数
        if method == 'GET':
            # 获取资源
            return self.get(request, *args, **kwargs)
        elif method == 'POST':
            # 更新资源
            return self.post(request, *args, **kwargs)
        elif method == 'PUT':
            # 添加资源
            return self.put(request, *args, **kwargs)
        elif method == 'DELETE':
            # 删除资源
            return self.delete(request, *args, **kwargs)
        else:
            # 不支持其他方法
            return method_not_allowed()
    
    def get(self, request, *args, **kwargs):
        return method_not_allowed()

    def post(self, request, *args, **kwargs):
        return method_not_allowed()

    def put(self, request, *args, **kwargs):
        return method_not_allowed()

    def delete(self, request, *args, **kwargs):
        return method_not_allowed()

class Register(object):
    def __init__(self, ):
        self.resources = []

    def register(self, resource):
        self.resources.append(resource)

    @property
    def urls(self):
        urlpatterns = [
            url(r'^{name}$'.format(name=resource.name), resource.enter) for resource in self.resources
        ]
        return urlpatterns


class SessionRest(Rest):
    def put(self, request, *args, **kwargs):
        data = request.PUT
        username = data.get('username', '')
        password = data.get('password', '')
        # 查询数据库用户表
        user = authenticate(username=username, password=password)
        if user:
            # 保存登录状态
            login(request, user)
            return json_response({
                'msg': '登录成功'
            })
        else:
            return params_error({
                'msg': '用户名或密码错误'
            })

    def delete(self, request, *args, **kwargs):
        logout(request)
        return json_response({
            'msg': '退出成功'
        })



class UserRest(Rest):
    def get(self, request, *args, **kwargs):
        user = request.user
        # 判断是否登录
        if user.is_authenticated:
            # 获取信息
            data = dict()
            if hasattr(user, 'customer'):
                customer = user.customer
                data['user'] = user.id
                data['category'] = 'customer'
                data['name'] = customer.name
                data['email'] = customer.email
                data['company'] = customer.company
                data['address'] = customer.address
                data['mobile'] = customer.mobile
                data['phone'] = customer.phone
                data['qq'] = customer.qq
                data['wechat'] = customer.wechat
                data['web'] = customer.web
                data['industry'] = customer.industry
                data['description'] = customer.description
            elif hasattr(user, 'userinfo'):
                userinfo = user.userinfo
                data['user'] = user.id
                data['category'] = 'userinfo'
                data['name'] = userinfo.name
                data['age'] = userinfo.age
                data['sex'] = userinfo.sex
                data['phone'] = userinfo.phone
                data['email'] = userinfo.email
                data['address'] = userinfo.address
                data['birthday'] = userinfo.birthday
                data['qq'] = userinfo.qq
                data['wechat'] = userinfo.wechat
                data['job'] = userinfo.job
                data['hobby'] = userinfo.hobby
                data['salary'] = userinfo.salary
            else:
                return json_response({})
        else:
            return not_authenticated()
        return json_response(data)
    def post(self, request, *args, **kwargs):
        # 判断用户是否登录
        data = request.POST
        user = request.user
        if request.user.is_authenticated:
            if hasattr(user, 'customer'):
                customer = user.customer
                customer.name = data.get('name', '')
                customer.email = data.get('email', '')
                customer.company = data.get('company', '')
                customer.address = data.get('address', '')
                customer.mobile = data.get('mobile', '')
                customer.phone = data.get('phone', '')
                customer.qq = data.get('qq', '')
                customer.wechat = data.get('wechat', '')
                customer.web = data.get('web', '')
                customer.industry =data.get('customer', '')
                customer.description = data.get('description', '')
                customer.save()
            elif hasattr(user, 'userinfo'):
                userinfo = user.userinfo
                userinfo.name = data.get('name', '')
                userinfo.age = data.get('age', '')
                userinfo.sex = data.get('sex', '')
                userinfo.email = data.get('email', '')
                userinfo.phone = data.get('phone', '')
                userinfo.address = data.get('address', '')
                userinfo.birthday = data.get('birthday', '')
                userinfo.qq = data.get('qq', '')
                userinfo.wechat = data.get('wechat', '')
                userinfo.hobby = data.get('hobby', '')
                userinfo.salary = data.get('salay', '')
                userinfo.save()
            else:
                return json_response({
                    'msg': '更新成功，恭喜'
                })
        else:
            return not_authenticated()
        return json_response({'msg': 'user post'})

    def put(self, request, *args, **kwargs):
        data = request.PUT
        username = data.get('username', '')
        password = data.get('password', '')
        ensure_password = data.get('ensure_password', '')
        regist_code = data.get('regist_code', 0)
        session_regist_code = request.session.get('regist_code', 1)
        error = dict()
        if not username:
            error['username'] = '必须提供用户名'
        else:
            if User.objects.filter(username=username).count() > 0:
                error['username'] = '用户名已存在'
        if len(password) < 6:
            error['password'] = '密码长度不可大于6位'
        if password != ensure_password:
            error['ensuer_password'] = '密码不匹配'
        if regist_code != session_regist_code:
            error['regist_code'] = '验证码不匹配'
        if error:
            return params_error(error)

        user = User()
        user.username = username
        user.set_password(password)
        user.save()

        category = data.get('category', 'userinfo')
        if category == 'userinfo':
            # 创建普通用户
            user_obj = UserInfo()
            user_obj.name = ''
            user_obj.age = 1
            user_obj.sex = 1
            user_obj.phone = ''
            user_obj.email = ''
            user_obj.address = ''
            user_obj.birthday = date(2018, 1, 1)
            user_obj.qq = ''
            user_obj.wechat = ''
            user_obj.hobby = ''
            user_obj.salary = ''
        else:
            # 创建客户
            user_obj = Customer()
            user_obj.name = ''
            user_obj.email = ''
            user_obj.company = ''
            user_obj.address = ''
            user_obj.mobile = ''
            user_obj.phone = ''
            user_obj.qq = ''
            user_obj.wechat = ''
            user_obj.web = ''
            user_obj.industry = ''
            user_obj.description = ''
        user_obj.user = user
        user_obj.save()
        return json_response({'id': user.id})



class RegistCode(Rest):
    def get(self, request, *args, **kwargs):
        # 获取6位随机数字
        regist_code = random.randint(100000, 1000000)
        # 保存到session中
        request.session['regist_code'] = regist_code
        # 返回随机数
        return json_response({
            'regist_code': regist_code
        })