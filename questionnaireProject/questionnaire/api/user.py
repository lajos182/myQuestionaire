import math
from datetime import datetime

from django.db.models import Q
from django.utils import timezone

from api.utils import *
from question.models import *
from api.decorators import *
from api.rest import Rest

# 问卷资源
class UserQuestionnaireRest(Rest):
    @userinfo_required
    def get(self, request, *args, **kwargs):
        data = request.GET
        limit = abs(int(data.get('limit', 15)))
        title = data.get('title', False)
        create_date = data.get('create_date', False)
        with_detail = data.get('with_detail', False)
        page = abs(int(data.get('page', 1)))

        Qs = [Q(state=4), Q(deadline__gte=datetime.now()), Q(free_count__gt=0)]

        if title:
            Qs.append(Q(title__contains=title))

        if create_date:
            create_date = datetime.strptime(create_date, '%Y-%m-%d')
            Qs.append(Q(create_date__gt=create_date))

        if limit > 50:
            limit = 50
        # 排除已参与的问卷
        joined = Answer.objects.filter(userinfo=request.user.userinfo)
        joined_ids = [obj.questionnaire.id for obj in joined]
        all_objs = Questionnaire.objects.filter(*Qs).exclude(id__in=joined_ids)
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
            # 将问卷添加到问卷列表中
            data.append(obj_dict)

        return json_response({
            'pages': pages,
            'objs': data
        })

# 用户参与问卷、用户退出参与
class UserQuestionnaireParticipation(Rest):
    @userinfo_required
    def put(self, request, *args, **kwargs):
        data = request.PUT
        questionnaire_id = data.get('questionnaire_id', 0)
        # 找出要参与的问卷
        questionnaire_exits = Questionnaire.objects.filter(
            id=questionnaire_id, state=4)
        if not questionnaire_exits:
            return params_error({
                'questionnaire_id': '当前问卷不存在'
            })

        # 判断是否已经参与了该问卷
        questionnaire = questionnaire_exits[0]
        has_joined = Answer.objects.filter(
            userinfo=request.user.userinfo, questionnaire=questionnaire)
        if has_joined:
            return params_error({
                'questionnaire_id': '已经参与了该问卷调查'
            })
        # 判断参与问卷的人数是否已满
        has_joined_count = Answer.objects.filter(
            questionnaire=questionnaire).count()
        if questionnaire.quantity <= has_joined_count:
            return params_error({
                'questionnaire_id': '该问卷参与人数已满'
            })
        # 判断问卷是否已经结束
        #  datetime.now() 不带时区 而从数据库中读取出来的时间是带时区的所以不能直接比较
        # 要使用django.utils timezone.now()
        if questionnaire.deadline < timezone.now():
            return params_error({
                'questionnaire_id': '该问卷已结束'
            })
        # 创建参与信息
        answer = Answer()
        answer.userinfo = request.user.userinfo
        answer.questionnaire = questionnaire
        answer.create_date = datetime.now()
        answer.is_done = False
        answer.save()
        # 更新可用问卷数量
        questionnaire.free_count = questionnaire.free_count - 1
        questionnaire.save()

        return json_response({
            'id': answer.id
        })

    @userinfo_required
    def delete(self, request, *args, **kwargs):
        data = request.DELETE
        ids = data.get('ids', [])
        objs = Answer.objects.filter(
            id__in=ids, userinfo=request.user.userinfo, is_done=False)
        deleted_ids = [obj.id for obj in objs]
        # 更新问卷可用数量
        for obj in objs:
            questionnaire = obj.questionnaire
            questionnaire.free_count = questionnaire.free_count+1
            questionnaire.save()
            # 删除用户选择该问卷的所有选项
            AnswerItem.objects.filter(userinfo=request.user.userinfo,item__question__questionnaire=questionnaire).delete()
        objs.delete()
        return json_response({
            'deleted_ids': deleted_ids
        })

# 用户提交选项、删除选项
class UserAnswerItemRest(Rest):
    @userinfo_required
    def put(self, request, *args, **kwargs):
        data = request.PUT
        userinfo = request.user.userinfo
        item_id = data.get('item_id', 1)
        item = QuestionItem.objects.get(id=item_id)
        if Answer.objects.filter(is_done=False, questionnaire=item.question.questionnaire, userinfo=userinfo).count() == 0:
            return params_error({
                "item_id": "不可提交该选项"
            })
        question = item.question
        if question.category == 'radio':
            AnswerItem.objects.filter(
                userinfo=userinfo, item__question=item.question).delete()
            answer_item = AnswerItem()
            answer_item.item = item
            answer_item.userinfo = userinfo
            answer_item.save()
        else:
            if AnswerItem.objects.filter(userinfo=userinfo, item=item).count() == 0:
                answer_item = AnswerItem()
                answer_item.item = item
                answer_item.userinfo = userinfo
                answer_item.save()
        return json_response({
            "msg": "选择成功"
        })

    @userinfo_required
    def delete(self, request, *args, **kwargs):
        data = request.DELETE
        item_id = data.get('item_id', 0)
        userinfo = request.user.userinfo
        item = QuestionItem.objects.get(id=item_id)
        if Answer.objects.filter(questionnaire=item.question.questionnaire, is_done=True, userinfo=userinfo):
            return params_error({
                "item_id": "不可删除该选项"
            })
        AnswerItem.objects.filter(
            item=item, userinfo=userinfo).delete()
        return json_response({
            "msg": "移除成功"
        })