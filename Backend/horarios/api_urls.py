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
    path('aulas/crear',crear_aula),
    #url para grupos:
    path('grupos/', grupos_list, name='_list'),
    #url para subir archivo
    path('upload/', ArchivoUploadView.as_view(), name='archivo-upload'),
    #horarios url:
    path('horarios/',horarios_list,name='horarios_list'),
    path('horario/crear', crear_horario, name='create_horario'),
    path('horario/<str:pk>', get_horario, name='get_horario'),
    path('horario/<str:pk>/', update_horario, name='update_horario'),
    path('horario/<str:pk>/', delete_horario, name='delete_horario'),
]