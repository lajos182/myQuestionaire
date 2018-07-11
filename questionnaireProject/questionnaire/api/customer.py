from datetime import datetime

from question.models import *
from api.decorators import *
from api.rest import Rest


class CustomerQuestionnaireRest(Rest):
    @customer_required
    def get(self, request, *args, **kwargs):
        data = request.GET
        id = data.get('id', None)
        page = abs(int(data.get('page', 1)))
        limit = abs(int(data.get('limit', 10)))
        with_detail = data.get('with_detail', False)
        questionnaires = Questionnaire.objects.filter(customer=request.user.customer).all()
        if id:
            questionnaire_objs = questionnaires[id]
        else:
            questionnaire_objs = questionnaires[(page - 1) * limit: page * limit]
        count = questionnaire_objs.count()
        data = []
        for obj in questionnaire_objs:
            # 构建单个问卷信息
            obj_dict = dict()
            obj_dict['id'] = obj.id
            obj_dict['title'] = obj.title
            obj_dict['quantity'] = obj.quantity
            obj_dict['create_date'] = datetime.strftime(obj.create_date, '%Y-%m-%d')
            obj_dict['deadline'] = datetime.strftime(obj.deadline, '%Y-%m-%d')
            obj_dict['state'] = obj.state
            obj_dict['customer'] = [{
                'id': obj.customer.id,
                'name': obj.customer.name
            }]
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
                        'id': item.id,
                        'content': item.content
                    } for item in question.questionitem_set.all()]
                    # 将问题添加到问题列表中
                    obj_dict['questions'].append(question_dict)
                obj_dict['comment'] = [{
                    'id': item.id,
                    'create_date': datetime.strftime(item.create_date, '%Y-%m-%d'),
                    'comment': item.comment
                } for item in obj.questionnairecheck_set.all()]
            # 将问卷添加到问卷列表中
            data.append(obj_dict)
        return json_response({
            'page': page,
            'count': count,
            'objs': data
        })

    @customer_required
    def post(self, request, *args, **kwargs):
        data = request.POST
        questionnaire = Questionnaire.objects.filter(customer=request.user.customer).get(id=data.get('id', 1))
        if questionnaire.state in [0, 2, 3]:
            questionnaire.title = data.get('title', '标题')
            questionnaire.free_count = data.get('free_count', 100)
            questionnaire.create_date = datetime.strftime(datetime.utcnow(), '%Y-%m-%d')
            questionnaire.state = 0
        questionnaire.save()
        return json_response({'msg': '更新成功'})

    @customer_required
    def put(self, request, *args, **kwargs):
        data = request.PUT
        title = data.get('title', '标题')
        deadline = datetime.strptime(data.get('deadline', ''), '%Y-%m-%d')
        quantity = data.get('quantity', 100)
        type = data.get('type', '')
        questionnaire = Questionnaire()
        questionnaire.customer = request.user.customer
        questionnaire.title = title
        questionnaire.deadline = deadline
        questionnaire.quantity = quantity
        questionnaire.type = type
        questionnaire.save()
        return json_response({'id': questionnaire.id})

    @customer_required
    def delete(self, request, *args, **kwargs):
        data = request.DELETE
        ids = data.get('ids', [])
        if len(ids) != 0:
            questionnaires = Questionnaire.objects.filter(customer=request.user.customer)
            for id in ids:
                questionnaires.get(id=id).delete()
            return json_response({'delete_ids': ids})
        else:
            return json_response({'msg': '未选择要删除的问卷'})

class CustomerQuestionRest(Rest):
    @customer_required
    def put(self, request, *args, **kwargs):
        data = request.PUT
        questionnaire_id = data.get('questionnaire_id', 0)
        questionnaire_exists = Questionnaire.objects.filter(id=questionnaire_id,customer=request.user.customer, state__in=[0, 2, 3])
        if questionnaire_exists:
            questionnaire = questionnaire_exists[0]
        else:
            return params_error({
                'questionnaire_id': '找不到问卷,或者问卷不可修改'
            })
        # 添加问题
        question = Question()
        question.questionnaire = questionnaire
        question.title = data.get('title', '题纲')
        question.category = data.get('category', 'radio')
        question.index = int(data.get('index', 0))
        question.save()
        # 修改问卷状态
        questionnaire.state = 0
        questionnaire.save()
        # 添加问题选项
        # items=['aaaa','bbbb','cccc','ddddd']
        items = data.get('items', [])

        for item in items:
            question_item = QuestionItem()
            question_item.question = question
            question_item.content = item
            question_item.save()

        return json_response({
            'id': question.id
        })

    @customer_required
    def post(self, request, *args, **kwargs):
        data = request.POST
        question_id = data.get('id', 0)
        # 判断需要修改的问题是否存在
        question_exits = Question.objects.filter(id=question_id, questionnaire__state__in=[
            0, 2, 3], questionnaire__customer=request.user.customer)
        if not question_exits:
            return params_error({
                'id': "该问题找不到,或者该问题所在问卷无法修改"
            })
        # 更新问题的属性
        question = question_exits[0]
        question.title = data.get('title', '题纲')
        question.category = data.get('category', 'radio')
        question.index = int(data.get('index', 0))
        question.save()
        # 更新问题所在问卷的状态
        questionnaire = question.questionnaire
        questionnaire.state = 0
        questionnaire.save()

        items = data.get('items', [])
        question.questionitem_set.all().delete()
        for item in items:
            question_item = QuestionItem()
            question_item.question = question
            question_item.content = item
            question_item.save()

        return json_response({
            'msg': '更新成功'
        })

    @customer_required
    def delete(self, request, *args, **kwargs):
        data = request.DELETE
        ids = data.get('ids', [])
        objs = Question.objects.filter(id__in=ids, questionnaire__state__in=[
            0, 2, 3], questionnaire__customer=request.user.customer)
        deleted_ids = [obj.id for obj in objs]
        questionnaire_set = set()
        for obj in objs:
            questionnaire_set.add(obj.questionnaire)

        for questionnaire in questionnaire_set:
            questionnaire.state = 0
            questionnaire.save()
        objs.delete()
        return json_response({
            'deleted_ids': deleted_ids
        })


class CustomerQuestionnaireStateRest(Rest):
    @customer_required
    def put(self, request, *args, **kwargs):
        data = request.PUT
        questionnaire_id = data.get('questionnaire_id', 0)
        state = data.get('questionnaire_state', False)
        if state == 0:
            questionnaire_exits = Questionnaire.objects.filter(
                id=questionnaire_id, customer=request.user.customer, state=0)
            if not questionnaire_exits:
                return params_error({
                    'questionnaire_id': '问卷找不到'
                })
            questionnaire = questionnaire_exits[0]
            questionnaire.state = 4
            questionnaire.save()
            return json_response({
                'state': "发布成功"
            })
        if state == 3:
            questionnaire_exits = Questionnaire.objects.filter(
                id=questionnaire_id, customer=request.user.customer, state=3)
            if not questionnaire_exits:
                return params_error({
                    'questionnaire_id': '问卷找不到'
                })
            questionnaire = questionnaire_exits[0]
            questionnaire.state = 4
            questionnaire.save()
            return json_response({
                'state': "发布成功"
            })
        return params_error({
            'questionnaire_id': '问卷找不到或当前状态不可修改'
        })


