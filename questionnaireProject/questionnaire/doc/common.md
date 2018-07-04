# 通用接口
## 获取验证码

method: GET

api: `/api/v1/register`

body: None

response:

```json
{
    "regist_code": 345693 //返回的验证码
}

```

## 用户接口

## 注册接口

method: PUT

api: `/api/v1/user`

body:
- **username**: 用户名
- **password**: 密码
- **ensure_password**: 确认密码
- **regist_code**: 注册码
- **category**: 注册的用户类型

response:

```json
{
    "id":1 //新建的用户id
}
```

## 获取用户信息

method: GET

api: `/api/v1/user`

body: None

response:
```json
{
    "user": 1, //用户id
    "category": "customer" //用户类型，可以是[`customer`, `userinfo`]
    "name": "千锋", //名称
    "email": "1000@phone.com", //邮箱
    "company": "华联科技有限公司", //公司名称
    "address": "河南省郑州市金水区", //地址
    "mobile": "15923459140", //手机号码
    "phone": "03987872549", //座机
    "qq": "123456", //QQ
    "wechat": "lajos_hunter", //微信号
    "web": "www.lajos.top", //网站地址
    "industry": "IT, 互联网", //行业
    "description": "公司是一家......" //公司简介
}
```
//或者
```json
{   
    "user": 1, //用户id
    "category": "customer" //用户类型，可以是[`customer`, `userinfo`]
    "name": "张三", //姓名
    "age": 18, //年龄
    "sex": 1, //性别，1→男, 2→女, 默认是1
    "phone": "18019100000", //手机号码
    "email": "zhangsan@163.com", //邮箱
    "address": "上海市浦东区", //地址
    "birthday": "date(1998, 12, 12)", //出生日期
    "qq": "12345678", //QQ
    "wechat": "zhangsan", //微信号
    "job": "IT工程师", //职业
    "hobby": "跑步, 游泳", //兴趣爱好
    "salary": "10k-20k" //收入水平    
}
```

### 更新用户信息

method: POST

api: `/api/v1/user`

body: 
- name: 名称
- email: 邮箱
- qq: QQ号
- .....

response:
```json
{
    "msg": "更新成功"
}
```

## 会话

### 登录

method: PUT

api: `/api/v1/session`

body:
- **username**: 用户名
- **password**: 密码

response:
```json
{
    "msg": "登录成功"
}
```

### 退出

method: DELETE

api: `api/v1/session`

body: None

response:
```json
{
    "msg": "退出成功"
}
```

