"""
# 管理员接口
"""

import math
from datetime import datetime


from django.db.models import Q


from question.models import *
from api.rest import Rest
from api.utils import *
from api.decorators import superuser_required

class AdminQuestionnaireRest(Rest):
    @superuser_required
    def get(self, request, *args, **kwargs):
        data = request.GET
        state = data.get('state', False)
        limit = abs(int(data.get('limit', 15)))
        title = data.get('title', False)
        create_date = data.get('create_date', False)
        with_detail = data.get('with_detail', False)
        page = abs(int(data.get('page', 1)))
        Qs = []
        if state:
            state = [int(state)]
        else:
            state = [0, 1, 2, 3, 4]
        Qs.append(Q(state__in=state))
        if title:
            Qs.append(Q(title__contains=title))
        if create_date:
            create_date = datetime.strptime(create_date, '%Y-%m-%d')
            Qs.append(Q(create_date__gt=create_date))
        if limit > 50:
            limit = 50
        all_objs = Questionnaire.objects.filter(*Qs)
        pages = math.ceil(all_objs.count()/limit) or 1
        if page > pages:
            page = pages
        start = (page-1)*limit
        end = page*limit
        objs = all_objs[start:end]
        data = []
        for obj in objs:
            # 构建单个问卷信息
            obj_dict = dict()
            obj_dict['id'] = obj.id
            obj_dict['title'] = obj.title
            obj_dict['create_date'] = datetime.strftime(
                obj.create_date, "%Y-%m-%d")
            obj_dict['deadline'] = datetime.strftime(obj.deadline, "%Y-%m-%d")
            obj_dict['state'] = obj.state
            obj_dict['quantity'] = obj.quantity
            obj_dict['free_count'] = obj.free_count
            obj_dict['customer'] = {
                "id": obj.customer.id,
                "name": obj.customer.name
            }
            if with_detail in ['true', True]:
                # 构建问卷下的问题
                obj_dict['questions'] = []
                for question in obj.question_set.all().order_by('index'):
                    # 构建单个问题
                    question_dict = dict()
                    question_dict['id'] = question.id
                    question_dict['title'] = question.title
                    question_dict['category'] = question.category
                    question_dict['index'] = question.index
                    # 构建问题选项
                    question_dict['items'] = [{
                        "id": item.id,
                        "content": item.content
                    } for item in question.questionitem_set.all()]
                    # 将问题添加到问卷的问题列表中
                    obj_dict['questions'].append(question_dict)
                obj_dict['comments'] = [{
                    'id': item.id,
                    'create_date': datetime.strftime(item.create_date, '%Y-%m-%d'),
                    'comment': item.comment
                } for item in obj.questionnairecomment_set.all().order_by('create_date')]
                obj_dict['suggests'] = [
                    {
                        "comment": item.comment,
                        "create_date": item.create_date.strftime('%Y-%m-%d')
                    }
                    for item in obj.questionnairesuggest_set.all()
                ]
            # 将问卷添加到问卷列表中
            data.append(obj_dict)
        return json_response({
            'pages': pages,
            'objs': data
        })

class QuestionnaireCheckRest(Rest):
    @superuser_required
    def put(self, request, *arg, **kwargs):
        data = request.PUT
        questionnaire_id = data.get('questionnaire_id')
        questionnaire_exits = Questionnaire.objects.filter(
            id=questionnaire_id, state=1)
        if not questionnaire_exits:
            return params_error({
                'questionnaire_id': '该问卷找不到,或者不可审核'
            })
        questionnaire = questionnaire_exits[0]
        is_agree = data.get('is_agree', False)
        comment = data.get('comment', '')
        if is_agree:
            questionnaire.state = 3
            questionnaire.save()
            return json_response({
                'comment': '审核通过'
            })
        if comment:
            questionnaire.state = 2
            questionnaire.save()
            questionnaire_comment = QuestionnaireCheck()
            questionnaire_comment.datetime = datetime.now()
            questionnaire_comment.comment = comment
            questionnaire_comment.questionnaire = questionnaire
            questionnaire_comment.save()
            return json_response({
                'comment': '提交审核内容成功'
            })
        return params_error({
            'comment': '没有提供审核信息'
        })



