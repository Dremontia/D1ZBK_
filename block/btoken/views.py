import hashlib
import json
import time

import jwt
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from user.models import UserProject


def tokens(request):
    """
    创建token -> 登录
    :param request:
    :return:
    """
    if not request.method == 'POST':
        result = {'code': 102, 'error': 'please userPost!'}
        return JsonResponse(result)
    # 获取登录信息
    json_str = request.body
    if not json_str:
        result = {'code': 101, 'error': 'please give json!'}
        return JsonResponse(result)
    json_obj = json.loads(json_str)

    username = json_obj.get('username')
    password = json_obj.get('password')
    # 确认用户名和密码是否为空
    if not username or not password:
        result = {'code': 103, 'error': 'Plase input username/password.'}
        return JsonResponse(result)
    # 检查用户名是否存在
    old_user = UserProject.objects.filter(username=username)
    if not old_user:
        result = {'code': 104, 'error': 'The username or password is wrong!!'}
        return JsonResponse(result)

    # 密码散列
    p_m = hashlib.sha256()
    p_m.update(password.encode())
    # p_m.hexdigest() 十六进制
    if old_user[0].password != p_m.hexdigest():
        result = {'code': 105, 'error': 'The username or password is wrong!!'}
        return JsonResponse(result)
    # token编码问题? byte 串不能json dumps 所以要执行decode方法
    token = make_token(username)

    result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}  # 出问题可能是没有decode
    return JsonResponse(result)


def make_token(username, expire=3600 * 24):
    """
    生成token
    :param username:
    :param expire:
    :return:
    """
    key = '123456'
    now_t = time.time()
    data = {'username': username, 'exp': int(now_t + expire)}
    return jwt.encode(data, key, algorithm='HS256')
