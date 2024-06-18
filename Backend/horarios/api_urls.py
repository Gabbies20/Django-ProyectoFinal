from django.urls import path
from  .api_views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

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
    path('profesores/crear',crear_profesor),
    path('profesores/editar/<str:id>',editar_profesor),
    #URL AULA:
    path('aulas/crear',crear_aula),
    #url para grupos:
    path('grupos/', grupos_list, name='_list'),
    #url para subir archivo
    path('upload/', ArchivoUploadView.as_view(), name='archivo-upload'),
    path('eliminar/archivo',borrar_archivoXML,name='eliminar_archivo'),
    #horarios url:
    path('horarios/',horarios_list,name='horarios_list'),
    path('horario/crear', crear_horario, name='create_horario'),
    path('horario/editar/<str:pk>', update_horario, name='actualizar_horario'),
    path('horarios/eliminar/<str:pk>',eliminar_horario),
    path('horario/<str:pk>', get_horario, name='get_horario'),
    path('horario/<str:pk>/', update_horario, name='update_horario'),
    #Usuarios:
    path('usuarios/',usuarios_list),
    #Url para Ausencias:
    path('ausencia/crear',crear_ausencia),
    path('profesor/asignaturas/',obtener_asignaturas),
    #Funcionalidades:
    path('horario/profesor/<str:id>',horario_profesor,name='horario_profesor'),
    path('horario/grupo/<str:id>',horario_grupo),
    path('guardias/', obtener_guardias_dia, name='obtener_guardias_dia'),
    path('ausencias/', obtener_ausencias, name='obtener_ausencias'),
    path('enviar-pdf/', enviar_pdf, name='enviar_pdf'),
    path('obtener_info_usuario/',obtener_info_usuario),
    #Login:
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('registrar/', registrar_usuario, name='registrar_usuario'),
]