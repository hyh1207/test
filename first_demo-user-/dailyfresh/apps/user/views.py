from django.shortcuts import render
from django.http import HttpResponse
import re
from user.models import User
from django.shortcuts import reverse, redirect
from django.views import View
from django.contrib.auth import login, logout, authenticate
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from itsdangerous import SignatureExpired


# def register(request):
#     '''注册'''
#
#     if request.method == 'GET':
#         '''显示注册页面'''
#
#         return render(request, 'register.html')
#
#     if request.method == 'POST':
#         '''注册处理'''
#
#         # 接收数据
#         username = request.POST.get('username')
#         password = request.POST.get('pwd')
#         email = request.POST.get('email')
#         allow = request.POST.get('allow')
#
#         # 数据校验
#         if not all([username, password, email]):
#             return render(request, 'register.html', {'errmsg': '数据不完整'})
#         # 校验邮箱
#         if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9]+(\.[a-z]{2,5}){1,2}$', email):
#             return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
#         # 是否同意协议
#         if allow != 'on':
#             return render(request, 'register.html', {'errmsg': '请同意协议'})
#         # 校验用户名是否重复
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             user = None
#
#         if user:
#             # 用户名已存在
#             return render(request, 'register.html', {'errmsg': '用户名已存在'})
#
#         # 进行业务处理：进行用户注册
#         user = User.objects.create_user(
#             username,
#             email,
#             password
#         )
#         # 返回应答，返回首页
#
#         return redirect(reverse('user:index'))


class RegisterView(View):
    '''注册'''

    def get(self, request):
        '''显示注册页面'''
        return render(request, 'register.html')

    def post(self, request):
        '''进行注册验证'''
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 数据校验
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
        # 是否同意协议
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})
        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 进行业务处理：进行用户注册
        user = User.objects.create_user(
            username,
            email,
            password
        )
        user.is_active = 0
        user.save()
        # 发送激活邮件，包含激活链接：http://127.0.0.1:8000/user/active/id
        # 激活连接中需要包含用户的身份信息  并且加密
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        # 返回应答，返回首页

        return redirect(reverse('user:register'))


class ActiveView(View):
    '''用户激活'''
    def get(self, request, token):
        ''' 进行用户激活'''
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取激活用户的id
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转到登陆页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
        # 激活连接已过期
        return HttpResponse('激活连接已过期')




def index(request):
    return render(request, 'index.html')


class Login(View):
    TEMPLATE = 'login.html'

    def get(self, request):

        error = request.GET.get('error', '')

        if 'username' in request.COOKIES:
            username = request.COOKIES['username']
        else:
            username = ''

        return render(request, self.TEMPLATE, {'error': error, 'username': username})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        exists = User.objects.filter(username=username).exists()
        print(username, password)

        if not exists:
            return redirect('/login?error=没有该用户')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
        else:
            return redirect('/login?error=密码错误')

        response = redirect('user:index')
        # 判断是否需要记住用户名
        print(remember)
        print(username)
        if remember == 'on':
            response.set_cookie('username', username, max_age=7*24*3600)

        return response


class LogoutUser(View):

    def get(self, request):

        logout(request)

        return redirect(reverse('user:login'))
