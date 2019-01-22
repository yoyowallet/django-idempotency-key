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
from django.conf.urls import url, include
from django.contrib import admin

from tests import views
from tests.viewsets import MyViewSet

urlpatterns = [
    url('admin/', admin.site.urls),

    url(r'^views/get/$', views.get),
    url(r'^views/create/$', views.create),
    url(r'^views/create-manual/$', views.create_manual),
    url(r'^views/create-exempt/$', views.create_exempt),
    url(r'^views/create-exempt-test-1/$', views.create_exempt_test_1),
    url(r'^views/create-exempt-test-2/$', views.create_exempt_test_2),
    url(r'^views/create-no-decorators/$', views.create_no_decorators),

    url(r'^viewsets/get/$', MyViewSet.as_view({'get': 'get'})),
    url(r'^viewsets/create/$', MyViewSet.as_view({'post': 'create'})),
    url(r'^viewsets/create-manual/$', MyViewSet.as_view({'post': 'create_manual'})),
    url(r'^viewsets/create-exempt/$', MyViewSet.as_view({'post': 'create_exempt'})),
    url(r'^viewsets/create-exempt-test-1/$', MyViewSet.as_view({'post': 'create_exempt_test_1'})),
    url(r'^viewsets/create-exempt-test-2/$', MyViewSet.as_view({'post': 'create_exempt_test_2'})),
    url(r'^viewsets/create-no-decorators/$', MyViewSet.as_view({'post': 'create_no_decorators'})),
]

urlpatterns = [url(r'^__debug__/', include(debug_toolbar.urls))] + urlpatterns
