"""Attendance_FacialRecognition URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.http import StreamingHttpResponse

from django.urls import path , include
from detector import views
from detector import detection_f_db as app_views


admin.site.site_header = 'FacialRecognition '
admin.site.site_title = 'FacialRecognition '
admin.site.index_title = 'FacialRecognition'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('<int:pk>/create_dataset',
         app_views.create_dataset, name="create_dataset"),
    path('trainer', app_views.trainer),
    path('detect', app_views.TrackImage),
    path('records/', include('detector.urls')),
]
