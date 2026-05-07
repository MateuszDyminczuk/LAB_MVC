"""
URL configuration for NaszaRemizaProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from remiza.admin import admin_site
from django.urls import path
from remiza.views import login_view
from remiza.views import index_view
from remiza.views import logout_view;

urlpatterns = [
    path('admin/', admin_site.urls),
    path('login/', login_view, name='login'),
    path('', index_view, name='index'),
    path('logout/', logout_view, name='logout'),
]
