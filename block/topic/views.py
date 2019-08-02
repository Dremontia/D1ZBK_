import html
import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from message.models import Message
from tools.login_check import login_check, get_user_by_requset
from topic.models import Topic
from user.models import UserProject


@login_check('POST')
def topics(request, author_id):
    if request.method == 'POST':

        json_str = request.body
        if not json_str:
            result = {'code': 305, 'error': 'Please give me data'}
            return JsonResponse(result)

        json_obj = json.loads(json_str)

        title = json_obj.get('title')
        if not title:
            result = {'code': 306, 'error': 'The title can not be none !'}
            return JsonResponse(result)
        # 防止xss 将可能为js语句改为普通文本转意 避免恶意攻击
        title = html.escape(title)
        category = json_obj.get('category')
        if not category:
            result = {'code': 307, 'error': 'The category can not be none !'}
            return JsonResponse(result)

        limit = json_obj.get('limit')
        if not limit:
            result = {'code': 308, 'error': 'The limit can not be none !'}
            return JsonResponse(result)

        # 带html标签样式的文章内容带颜色粗细
        content = json_obj.get('content')
        if not content:
            result = {'code': 309, 'error': 'The content can not be none !'}
            return JsonResponse(result)

        # 纯文本的文章内容 用于截取简介
        content_text = json_obj.get('content_text')
        if not content_text:
            result = {'code': 310, 'error': 'The content_text can not be none!'}
            return JsonResponse(result)

        # 截取30长度的文章作为简介
        introduce = content_text[:30]

        if request.user.username != author_id:
            result = {'code': 311, 'error': 'Can not such me!!'}
            return JsonResponse(result)
        # 创建数据
        try:
            Topic.objects.create(title=title, category=category,
                                 limit=limit, content=content,
                                 introduce=introduce, author_id=author_id)
        except:
            result = {'code': 312, 'error': 'Topic is rest .'}
            return JsonResponse(result)

        result = {'code': 200, 'username': request.user.username}
        return JsonResponse(result)

    elif request.method == 'GET':
        # 访问着 visitor
        # 博主/作者 author
        author = UserProject.objects.filter(username=author_id)
        # 查找博主
        if not author:
            result = {'code': 313, 'error': 'The user in not existed !'}
            return JsonResponse(result)
        author = author[0]

        # 查找我们的访问者
        visitor = get_user_by_requset(request)
        visitor_username = None
        if visitor:
            visitor_username = visitor.username

        t_id = request.GET.get('t_id')
        if t_id:
            t_id = int(t_id)
            is_self = False
            if visitor_username == author.username:
                # 博主正在访问自己的博客
                is_self = True
                try:
                    author_topic = Topic.objects.get(id=t_id)
                except Exception as e:
                    result = {'code': 314, 'error': 'no topic'}
                    return JsonResponse(result)


            else:
                # 陌生的访问者 在访问博主的博客
                try:
                    author_topic = Topic.objects.get(id=t_id, limit='public')
                except Exception as e:
                    result = {'code': 315, 'error': 'no topic!'}
                    return JsonResponse(result)

            res = make_topic_res(author, author_topic, is_self)

            return JsonResponse(res)

        else:
            # 判断是否有查询字符串[category]
            category = request.GET.get('category')
            if category in ['tec', 'no-tec']:
                if visitor_username == author.username:
                    # 博主正在访问自己的博客
                    author_topics = Topic.objects.filter(author_id=author.username, category=category)
                else:
                    # 陌生的访问者 在访问博主的博客
                    author_topics = Topic.objects.filter(author_id=author.username, limit='public',
                                                         category=category)

                result = make_topics_res(author, author_topics)
                return JsonResponse(result)
            else:
                if visitor_username == author.username:
                    # 博主正在访问自己的博客
                    author_topics = Topic.objects.filter(author_id=author.username)
                else:
                    # 陌生的访问者 在访问博主的博客
                    author_topics = Topic.objects.filter(author_id=author.username, limit='public')

                result = make_topics_res(author, author_topics)
                return JsonResponse(result)

    elif request.method == 'DELETE':
        # 删除博客 [真删除]
        # 查询字符串中 包含 topic_id

        pass


# 返回值
def make_topics_res(author, author_topics):
    res = {'code': 200, 'data': {}}
    topics_res = []
    for topics in author_topics:
        d = {}
        d['id'] = topics.id
        d['title'] = topics.title
        d['category'] = topics.category
        d['created_time'] = topics.created_time.strftime('%Y-%m-%d %H:%M:%S')
        d['introduce'] = topics.introduce
        d['author'] = author.nickname
        topics_res.append(d)
    res['data']['topics'] = topics_res
    res['data']['nickname'] = author.nickname
    return res


def make_topic_res(author, author_topic, is_self):
    '''
    生成 topic 详情数据
    :param author:
    :param author_topic:
    :param is_self:
    :return:
    '''
    if is_self:
        # 当前是博主访问自己的博客
        # 下一个为 id大于自身的第一个id
        # 上一个 小于自身的最后一个id
        next_topic = Topic.objects.filter(id__gt=author_topic.id,
                                          author=author).first()
        last_topic = Topic.objects.filter(id__lt=author_topic.id,
                                          author=author).last()
    else:
        next_topic = Topic.objects.filter(id__gt=author_topic.id,
                                          author=author, limit='public').first()
        last_topic = Topic.objects.filter(id__lt=author_topic.id,
                                          author=author, limit='public').last()
    # 生成下一个文章的id和title
    if next_topic:
        next_id = next_topic.id
        next_title = next_topic.title
    else:
        next_id = None
        next_title = None

    # 生成上一个文章的id和title
    if last_topic:
        last_id = last_topic.id
        last_title = last_topic.title
    else:
        last_id = None
        last_title = None
    all_message = Message.objects.filter(topic=author_topic).order_by('-created_time')
    # 按照时间倒叙 不要写错最后的蒂选方法

    message = []
    msg_dict = {}
    for i in all_message:
        # 留言
        if i.parent_message == 0:
            message.append({'id': i.id,
                            'content': i.content,
                            'publisher': i.publisher.nickname,
                            'publisher_avatar': str(i.publisher.avatar),
                            'created_time': i.created_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'reply': []})

        # 回复
        elif i.parent_message != 0:
            if i.parent_message in msg_dict:
                msg_dict[i.parent_message].append({'msg_id': i.id,
                                                   'publisher': i.publisher.nickname,
                                                   'publisher_avatar': str(i.publisher.avatar),
                                                   'content': i.content,
                                                   'created_time': i.created_time.strftime('%Y-%m-%d %H:%M:%S')})
            else:
                msg_dict[i.parent_message] = []
                msg_dict[i.parent_message].append({'msg_id': i.id,
                                                   'publisher': i.publisher.nickname,
                                                   'publisher_avatar': str(i.publisher.avatar),
                                                   'content': i.content,
                                                   'created_time': i.created_time.strftime('%Y-%m-%d %H:%M:%S')})

    # 关联 留言和对应的回复
    # message  -> [{留言相关的信息, 'reply':[]},]

    for m in message:
        if m['id'] in msg_dict:
            m['reply'] = msg_dict[m['id']]

    result = {'code': 200, "data": {}}

    result['data']['nickname'] = author.nickname
    result['data']['title'] = author_topic.title
    result['data']['category'] = author_topic.category
    result['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
    result['data']['content'] = author_topic.content
    result['data']['introduce'] = author_topic.introduce
    result['data']['author'] = author.nickname
    result['data']['next_id'] = next_id
    result['data']['next_title'] = next_title
    result['data']['last_id'] = last_id
    result['data']['last_title'] = last_title

    # 留言回复数据
    result['data']['messages'] = message
    result['data']['messages_count'] = len(message) + len(msg_dict)

    return result
