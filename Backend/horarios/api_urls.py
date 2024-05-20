from django.urls import path

from  .api_views import *

urlpatterns = [
    path('profesores/', profesores_list, name='profesores_list'),
    path('aulas/', aulas_list, name='aulas_list'),
    
    path('horarios/',horarios_list,name='horarios_list'),
    path('grupos/',grupos_list,name='grupos_list'),
     path('franjas/',franjas_list,name='franjas_list'),
    path('datos/', xml_data_view, name='xml-data'),
    path('asignaturas/', asignaturas_list, name='asignaturas_list'),
    path('asignaturas/crear',crear_asignatura),
    path('asignaturas/editar/<str:id>',editar_asignatura),
    path('asignaturas/eliminar/<str:id>',eliminar_asignatura),
    path('asignatura/<str:asignatura_cod>',asignaturas_obtener),
    #urls para profesores:
    path('profesores/', profesores_list, name='profesores_list'),
    path('profesor/<str:id>',profesores_obtener),
    #URL AULA:
    path('aulas/crear',crear_aula)
]