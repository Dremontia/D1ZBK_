import jwt
from django.http import JsonResponse

from user.models import UserProject

TOKEN_KEY = '123456'


def login_check(*methods):
    def _login_check(func):
        def wrapper(request, *args, **kwargs):
            # 获取token
            token = request.META.get('HTTP_AUTHORIZATION')
            if not methods:
                # 如果当前没传任何参数,则直接返回视图函数
                return func(request, *args, **kwargs)
            else:
                # 检查当前request.method 是否在参数列表中
                if request.method not in methods:
                    return func(request, *args, **kwargs)

            if not token:
                result = {'code': 109, 'error': 'Please gime me token!!'}
                return JsonResponse(result)

            try:
                res = jwt.decode(token, TOKEN_KEY)
            # except jwt.ExpiredSignatureError 超时
            except Exception as e:
                print('login check is error %s' % (e))
                result = {'code': 108, 'error': 'The token is wrong!!'}
                return JsonResponse(result)

            # token 校验成功
            username = res['username']

            try:
                user = UserProject.objects.get(username=username)
            except:
                user = None
            if not user:
                result = {'code': 110, 'error': 'The user is not existed'}
                return JsonResponse(result)

            # 请传给视图层
            request.user = user
            return func(request, *args, **kwargs)

        return wrapper

    return _login_check


def get_user_by_requset(request):
    """
    通过request 获取 user
    :param request:
    :return:
    """
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None

    # 尝试性的解析token
    try:
        res = jwt.decode(token, TOKEN_KEY)
    except:
        return None

    username = res['username']

    try:
        user = UserProject.objects.get(username=username)
    except:
        return None

    if not user:
        return None

    return user
