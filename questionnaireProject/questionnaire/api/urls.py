# 导入Python自带的包放在最顶层(一般放在最顶层)
import os

# 导入第三方扩展包
from django.conf.urls import url

# 导入工程内部的相关包
from api.rest import *
from api.customer import *
from api.admin import *
from api.user import *

# # 新建session对象
# session_obj = SessionRest()
# # 新建user对象
# user_obj = UserRest()
# api_urls = [
#     url(r'session', session_obj.enter),
#     url(r'user', user_obj.enter),
# ]

api = Register()
api.register(SessionRest('session'))
api.register(UserRest('user'))
api.register(RegistCode())
api.register(CustomerQuestionnaireRest('customer_questionnaire'))
api.register(CustomerQuestionRest('customer_question'))
api.register(AdminQuestionnaireRest('admin_questionnaire'))
api.register(QuestionnaireCheckRest('questionnaire_comment'))
api.register(UserQuestionnaireRest('user_questionnaire'))
api.register(UserQuestionnaireParticipation('participation'))
