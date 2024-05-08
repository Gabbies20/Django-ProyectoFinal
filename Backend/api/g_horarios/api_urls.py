from django.urls import path

from  .api_views import *

urlpatterns = [
    path('profesores',profesores_list, name='profesores_list'),
]