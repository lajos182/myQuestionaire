# 用户接口

## 用户查看问卷

method: GET

api: '/api/v1/user_questionnaire'

params:
- page: 第几页数据，默认1
- limit: 每页数据默认10
- status: 状态， 默认草稿
- with_detail: 是否需要详情，默认False
- id：问卷id，默认空

respond：
```json
{
    "pages":100,//总页数
    "count":8888,//问卷总数
    "objs":[//问卷列表
        {
            "id": 1,//问卷id
            "title": "测试问卷",//问卷标题
            "quantity":100,//问卷数量
            "free_quantity":100,//剩余问卷数量
            "expire_date":"2018-12-10",//问卷截止时间
            "create_date":"2018-7-4",//问卷创建时间
            "status":0,//问卷状态：0->草稿，1->待审核，2->审核失败，3->审核通过，4->已发布
            "customer":{
                "id":1,//
                "name":""//
            },
            "questions":[
                {
                    "id":1,//选项id
                    "title":"问题1",//问题标题
                    "category":"radio",//问题类型，radio为单选，checkbox为多选
                    "items":[
                        {
                            "id": 1,//选项id
                            "content":"选项1",//选项1
                        }
                    ]
                },
                
            ],
            "comments":[//批注信息
                {
                    "id":1,//批注id
                    "create_date":"2018-7-5",//批注日期
                    "content":"测试批注不通过",//批注内容
                }
            ]
        }
    ]
}
```
 
## 参与信息

### 参与问卷

method: PUT

api: '/api/v1/participation'

body:
- **questionnaire_id**: 问卷id

response:
```json
{
  "msg":"参与成功"
}
```

### 退出参与

method: DELETE

api: '/api/v1/participation'

body:

- **ids**: 参与信息id列表，例如ids:[1,2,3]

response:
```json
{
  "delete_ids":[2,3]
}
```

## 用户查看参与信息

method: GET

api: `/api/v1/participation`

body:
- state: 参与信息状态, 默认False
- page: 第几页，默认1
- limit: 每业数量， 默认10

response:
```json
{
    "questionnaire": {
        "title": "问卷1" //问卷标题
    },
    "join_date": "2018-10-10", //参与时间
    "state": false //参与状态，false未完成，true已完成
}
```

## 答案

### 提交答案

method: PUT

api: '/api/v1/answer'

body:
- **item_id**:选项id

response:
```json
{
  "msg":"提交成功"
}
```


### 删除答案

method: DELETE

api: '/api/v1/answer'

body:
- **item_ids**: 选项id列表，如ids:[1,2,3]

response:
```json
{
  "delete_ids":[2,3]
}
```

## 用户查看问卷答案

method: GET

api: `/api/v1/user_answer`

body:
- **questionnaire_id**: 问卷id

response:
```json
{
    "questionnaire": {
        "title": "测试问卷", //问卷标题
        "deadline": "2018-10-10", //问卷截止信息
        "customer": "前锋" //问卷所属客户名称
    },
    "questions": [
        {
            "title": "问题1", //问题
            "category": "radio", //问题类型，radio单选，select多选
            "id": 1, //问题id
            "items": [
                {
                    "id": 1, //选项id
                    "content": "选项1", //选项内容
                    "is_select": false //是否选择了选项
                },
                ......
            ]
        }
    ]
}
```

## 用户完成答题

method: POST

api: `/api/v1/user_participation_state`

body:
- **questionnaire_id**: 问卷id

response:
```json
{
    "msg": "提交成功"
}
```

## 用户查看积分

method: GET

api: `/api/v1/user_point_history`

body:
- category: 积分类型，false代表消费，true代表获取，默认true
- page: 第几页， 默认1
- limit: 每页数量，默认10

response:
```json
{
    "balance": 1000, //用户积分数量
    "history": [
        {
            "create_date": "2018-10-10", //历史时间
            "amount": 10, //数量
            "reason": "提交问卷" //原因
        },
        ......
    ]
}
```
