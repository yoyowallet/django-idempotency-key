"""tests URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin

from tests import views

urlpatterns = [
    url('admin/', admin.site.urls),
    url('get-voucher/', views.get_voucher),
    url('create-voucher/', views.create_voucher),
    url('create-voucher-manual/', views.create_voucher_manual),
    url('create-voucher-exempt/', views.create_voucher_exempt),
    url('create-voucher-use-idempotency-key/', views.create_voucher_use_idempotency_key),
    url('create-voucher-exempt-test-1', views.create_voucher_exempt_test_1),
    url('create-voucher-exempt-test-2', views.create_voucher_exempt_test_2),
    url('create-voucher-no-decorators', views.create_voucher_no_decorators)
]
