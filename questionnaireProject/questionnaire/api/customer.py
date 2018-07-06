from datetime import datetime

from api.utils import *
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
        state = data.get('state', 0)
        with_detail = data.get('with_detail', False)
        questionnaires = Questionnaire.objects.filter(customer=request.user.customer).all()
        data = dict()
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