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

import debug_toolbar
from django.conf.urls import include
from django.contrib import admin
from django.urls import path

from tests import views
from tests.viewsets import MyViewSet, MyViewSet2, MyViewSet2Exempt

urlpatterns = [
    path("admin/", admin.site.urls),
    path(r"views/get/", views.get),
    path(r"views/create/", views.create),
    path(r"views/create-manual/", views.create_manual),
    path(r"views/create-exempt/", views.create_exempt),
    path(r"views/create-exempt-test-1/", views.create_exempt_test_1),
    path(r"views/create-exempt-test-2/", views.create_exempt_test_2),
    path(r"views/create-no-decorators/", views.create_no_decorators),
    path(r"views/create-manual-exempt-1/", views.create_manual_exempt_1),
    path(r"views/create-manual-exempt-2/", views.create_manual_exempt_2),
    path(r"views/create-with-my-cache/", views.create_with_my_cache),
    path(r"views/create-custom-header/", views.create_custom_header),
    path(r"viewsets/get/", MyViewSet.as_view({"get": "get"})),
    path(r"viewsets/create/", MyViewSet.as_view({"post": "create"})),
    path(
        r"viewsets/create-optional/",
        MyViewSet.as_view({"post": "create_optional"}),
    ),
    path(r"views/create-manual-exempt-2/", views.create_manual_exempt_2),
    path(r"viewsets/create-manual/", MyViewSet.as_view({"post": "create_manual"})),
    path(r"viewsets/create-exempt/", MyViewSet.as_view({"post": "create_exempt"})),
    path(
        r"viewsets/create-exempt-test-1/",
        MyViewSet.as_view({"post": "create_exempt_test_1"}),
    ),
    path(
        r"viewsets/create-exempt-test-2/",
        MyViewSet.as_view({"post": "create_exempt_test_2"}),
    ),
    path(
        r"viewsets/create-no-decorators/",
        MyViewSet.as_view({"post": "create_no_decorators"}),
    ),
    path(
        r"viewsets/create-manual-exempt-1/",
        MyViewSet.as_view({"post": "create_manual_exempt_1"}),
    ),
    path(
        r"viewsets/create-manual-exempt-2/",
        MyViewSet.as_view({"post": "create_manual_exempt_2"}),
    ),
    path(
        r"viewsets/create-with-my-cache/",
        MyViewSet.as_view({"post": "create_with_my_cache"}),
    ),
    path(
        r"viewsets/create-nested-decorator/",
        MyViewSet2.as_view({"post": "create"}),
    ),
    path(
        r"viewsets/create-nested-decorator-exempt/",
        MyViewSet2Exempt.as_view({"post": "create"}),
    ),
]

urlpatterns = [path(r"__debug__/", include(debug_toolbar.urls))] + urlpatterns
