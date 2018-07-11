# 支付回调接口

method: [GET, POST]

body:
- **order_ids**: 内部订单号
- **amount**: 支付金额
- **state**: 是否支付成功

response:根据第三方需求，返回相应的数据