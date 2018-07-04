# 客户端口
## 问卷接口

## 创建问卷

method: PUT

api: `/api/v1/customer_questionnaire`

body:
- **customer**: 客户id
- **title**: 问卷标题
- **create_date**: 创建时间, 格式是: YYYY-MM-DD, 例如: 2018-7-4
- **deadline**: 截止时间, 格式是: YYYY-MM-DD, 例如: 2018-10-20
- **quantity**: 数量
- **free_count**: 可用问卷数量
- **state**: 状态，0→草稿,1→待审核,2→审核失败,3→审核通过,4→已发布
- **type**: 问卷类型

response:
```json
{
    "id": 1 //新建的问卷id
}
```
## 更新问卷

method: POST

api: `/api/v1/customer_questionnaire`

body:
- **customer**: 客户id
- **title**: 问卷标题
- **create_date**: 创建时间, 格式是: YYYY-MM-DD, 例如: 2018-7-4
- **deadline**: 截止时间, 格式是: YYYY-MM-DD, 例如: 2018-10-20
- **quantity**: 数量
- **free_count**: 可用问卷数量
- **state**: 状态，0→草稿,1→待审核,2→审核失败,3→审核通过,4→已发布
- **type**: 问卷类型

response:
```json
{
    "msg": "更新成功"
}
```

## 删除问卷

method: DELETE

api: `/api/v1/customer_questionnaire`

body:
- **ids**: 删除的问卷id列表, 例如{"ids": [1, 2, 3, 4]}

response:
```json
{
    "delete_ids": [2, 4] //被删除的id列表
}
```

## 获取问卷
method: GET

api: `/api/v1/customer_questionnaire`

params:
- page: 第几页数据, 默认1
- limit: 每页数量, 默认10
- status: 状态, 默认草稿
- with_detail: 是否需要详情, 默认False
- id: 问卷id, 默认空

response:
```json
{
    "page": 100, //总页数
    "count": 8888, //问卷数量
    "objs": [ //问卷列表
        {
            "id": 1, //问卷id
            "title": "测试问卷", //问卷标题
            "quantity": 100, //问卷数量
            "expire_date": "2018-12-10", //问卷截止日期
            "create_date": "2018-7-4", //问卷创建时间
            "status": 0, //问卷状态: 0→草稿, 1→待审核, 2→审核失败, 3→审核通过, 4→已发布
            "customer": {
                "id": 1, //客户id
                "name": "千锋" //客户名称
            },
            // 加入with_detail参数为True,那么包含有以下信息
            "question": [
                {
                    "id": 1, //问题id
                    "title": "问题1", //问题标题
                    "category": "radio", //问题类型， radio为单选， ceheckbox为多选
                    "items": [
                        {
                            "id": 1, //问题id
                            "content": "选项1" //选项内容
                        }
                    ]
                },
                ......
            ],
            "comments": [ //批注信息
                {
                    "id": 1, //批注id
                    "create_date": "2018-7-5", //批注日期
                    "content": "测试批注不通过" //批注内容
                }
                ......
            ]
        }
        ......
    ]
}
```