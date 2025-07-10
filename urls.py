"""
URL configuration for headhunter project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from app01 import views

urlpatterns = [
    # 主页
    path('home/', views.home),
    # 登录页面
    path('login/', views.login),
    # 注册页面
    path('register/', views.register),
    # 修改密码页面
    path('set_password/', views.set_password),
    # 退出登录
    path('logout/', views.logout),
    # 选择难度
    path('choice_hard/', views.choice_hard),
    # 开始挑战
    path('start/', views.start),
    # 无用的数据存储
    path('get_data/', views.get_data),
    path('index/', views.index),
    # 历史数据
    path('history/', views.history),
    
    # path('my_view/', views.my_view),
    re_path(r'^$', views.xxxx)


]
