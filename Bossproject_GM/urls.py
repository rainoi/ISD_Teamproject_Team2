"""Bossproject_GM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
import management.views
from management.views import logout



urlpatterns = [
    path("admin/", admin.site.urls),
    path('', management.views.login, name="login"),
    path('gowork/', management.views.gowork, name="gowork"),
    path('gohome/', management.views.gohome, name="gohome"),
    path('auth/', include('social_django.urls', namespace='social')),
    path('mgmt/', include('management.urls')),
    path('logout/', logout, name='logout'),

]