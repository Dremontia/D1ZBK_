import jwt
from django.http import JsonResponse
import json

from btoken.views import make_token
from .models import *
import hashlib
from tools.login_check import login_check


# Create your views here.

@login_check('PUT')
def users(request, username=None):
    if request.method == 'POST':
        # 注册
        json_str = request.body
        if not json_str:
            result = {'code': 202, 'error': 'please POST data !!!'}
            return JsonResponse(result)
        # 如果当前报错,请执行 json_str = json_str.decode()
        json_obj = json.loads(json_str)

        username = json_obj.get('username')
        email = json_obj.get('email')
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')

        if not username:
            result = {'code': 203, 'error': 'Plase input username.'}
            return JsonResponse(result)

        if not email:
            result = {"code": 204, 'error': 'Plase input email.'}

        if not password_1 or not password_2:
            result = {"code": 205, 'error': 'Plase input password.'}
            return JsonResponse(result)

        if password_2 != password_1:
            result = {'code': 206, 'error': 'password is not defind.'}

        # 检查用户名是否存在
        old_user = UserProject.objects.filter(username=username)
        if old_user:
            result = {'code': 207, 'error': 'The usename is not fine!!!'}
            return JsonResponse({'code': 200})

        # 密码散列
        p_m = hashlib.sha256()
        p_m.update(password_1.encode())

        try:
            UserProject.objects.create(username=username,
                                       nickname=username,
                                       email=email,
                                       password=p_m.hexdigest())
        except Exception as e:
            print('----create error is %s' % (e))
            result = {'code': 500, 'error': 'Sorry, server is busy!'}
            return JsonResponse(result)
        # token编码问题? byte 串不能json dumps 所以要执行decode方法
        token = make_token(username)

        result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}  # 出问题可能是没有decode
        return JsonResponse(result)

    # 127.0.0.1:5000/register
    elif request.method == 'GET':
        # s = json.dumps({'code': 200})
        # return HttpResponse(s)
        # 获取数据
        if username:
            # 获取指定用户数据
            old_user = UserProject.objects.filter(username=username)

            if not old_user:
                result = {'code': 401, 'error': 'not this user'}
                return JsonResponse(result)
            old_user = old_user[0]
            if request.GET.keys():
                # 当前请求有查询字符串
                data = {}
                for key in request.GET.keys():
                    if key == 'password':
                        # 如果查询密码,则continue!
                        continue

                    # hasattr 第一个参数为对象,第二个参数为属性字符串 -> 若对象
                    # 含有第二个参数的属性,则返回True返回False
                    # getattr 参数同hasattr,若对象含有第二个参数的属性则返回对应
                    # 属性的值,反之抛出异常AttributeError
                    if hasattr(old_user, key):
                        if key == 'avatar':
                            data[key] = str(getattr(old_user, key))
                        else:
                            data[key] = getattr(old_user, key)
                result = {'code': 200, 'username': username, 'data': data}
                return JsonResponse(result)
            else:
                # 无查询字符串,即获取制定用户所有数据
                result = {'code': 200, 'username': username, 'data':
                    {'info': old_user.info,
                     'sign': old_user.sign,
                     'nickname': old_user.nickname,
                     'avatar': str(old_user.avatar)}}
                return JsonResponse(result)
        else:
            # 没有username
            all_users = UserProject.objects.all()
            result = []
            for _user in all_users:
                d = {}
                d['username'] = _user.username
                d['nickname'] = _user.nickname
                d['sign'] = _user.sign
                d['info'] = _user.info
                d['email'] = _user.email
                d['avatar'] = str(_user.avatar)
                result.append(d)
            return JsonResponse({'code': 200,
                                 'data': result})

    elif request.method == 'PUT':
        # http://127.0.0.1:8000/v1/users/<username>
        # 更新用户数据
        user = request.user

        json_str = request.body
        json_obj = json.loads(json_str)

        nickname = json_obj.get('nickname')
        if not nickname:
            result = {'code': 210, 'error': 'The nickname can not be none !'}
            return JsonResponse(result)

        sign = json_obj.get('sign')
        if sign is None:
            result = {'code': 211, 'error': 'The sign not in json'}
            return JsonResponse(result)

        info = json_obj.get('info')
        if info is None:
            result = {'code': 211, 'error': 'The info not in json'}
            return JsonResponse(result)

        if user.username != username:
            result = {'code': 213, 'error': 'This is wrong!!!'}
            return JsonResponse(result)

        user.sign = sign
        user.info = info
        user.nickname = nickname
        user.save()
        result = {'code': 200, 'username': username}
        return JsonResponse(result)


@login_check('POST')
def avatar(request, username):
    # 当前只开放post请求
    if request.method != 'POST':
        result = {'code': 214, 'error': 'Please use POST'}
        return JsonResponse(result)
    user = request.user
    if user.username != username:
        # 异常请求
        result = {'code': 215, 'error': 'You are wrong!!!'}
        return JsonResponse(result)

    # 获取图片,上传方式是表单提交
    # avatar = request.FILES.get('avatar')

    avatar = request.FILES['avatar']
    if not avatar:
        result = {'code': 216, 'error': 'Please give me avatar!!!'}
        return JsonResponse(result)
    # 更新
    user.avatar = avatar
    user.save()
    result = {'code': 200, 'username': username}
    return JsonResponse(result)

# def check_token(request):
#     token = request.META.get('HTTP_AUTHORIZATION')
#     if not token:
#         return None
#
#     try:
#         res = jwt.decode(token, '123456')
#     except Exception as e:
#         print('check_token error is %s' % (e))
#         return None
#
#     username = res['username']
#     users = UserProject.objects.filter(username=username)
#     return users[0]
