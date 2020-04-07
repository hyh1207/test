from django.urls import path
from user.views import RegisterView, index, Login, LogoutUser, ActiveView
from django.conf.urls import url


app_name = 'user'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # path('register/', views.register.as_view(), name='register'),
    path('index/', index, name='index'),
    path('login/', Login.as_view(), name='login'),
    path('logout', LogoutUser.as_view(), name='logout'),
    # url(r'^active/(.*)$', ActiveView.as_view, name='active')
    path('active/<str:token>', ActiveView.as_view, name='active')  # 用户激活
]
