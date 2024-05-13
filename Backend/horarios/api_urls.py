from django.urls import path

from  .api_views import *

urlpatterns = [
    path('profesores/', profesores_list, name='profesores_list'),
    path('aulas/', aulas_list, name='aulas_list'),
    path('asignaturas/', asignaturas_list, name='asignaturas_list'),
    path('datos/', xml_data_view, name='xml-data'),
    path('asignaturas/crear',crear_asignatura)
]