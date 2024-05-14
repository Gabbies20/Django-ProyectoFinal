from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import FileResponse, HttpResponse
from .serializers import AsignaturaSerializer
import xml.etree.ElementTree as ET
from django.conf import settings
import os
from rest_framework import status

#from .forms import *




@api_view(['GET'])
def profesores_list(request):
   profesores = Profesor.objects.all()
   serializer = ProfesorSerializer(profesores, many=True)
   return Response(serializer.data)



@api_view(['GET'])
def aulas_list(request):
   aulas = Aula.objects.all()
   serializer= AulaSerializer(aulas, many=True)
   return Response(serializer.data)



@api_view(['GET'])
def asignaturas_list(request):
    asignaturas = Asignatura.objects.all()
    serializer= AsignaturaSerializer(asignaturas, many=True)
    return Response(serializer.data)


def xml_data_view(request):
    xml_file_path = os.path.join(settings.BASE_DIR, 'datos.xml')
    return FileResponse(open(xml_file_path, 'rb'))
 
 
#ASIGNATURAS:
@api_view(['POST'])
def crear_asignatura(request):
    serializers = AsignaturaSerializerCreate(data=request.data)
    if serializers.is_valid():
        try:
            serializers.save()
            return Response("Asignatura creada")
        except Exception as error:
            return Response(error, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializers.errors, status = status.HTTP_400_BAD_REQUEST)
 


# @api_view(['GET'])
# def asignaturas_list(request):
#     # Ruta al archivo XML
#     xml_file_path = os.path.join(settings.BASE_DIR, 'datos.xml')
#     print(xml_file_path)

#     # Parsear el archivo XML
#     tree = ET.parse(xml_file_path)
#     root = tree.getroot()
#     print(root)

#     # Lista para almacenar las asignaturas
#     asignaturas = []

#     # Iterar sobre los elementos XML y extraer las asignaturas
#     for table_element in root.findall('table'):
#         if table_element.get('name') == 'asignaturas':
#             asignatura_cod = None
#             descripcion = None
#             for column_element in table_element.findall('column'):
#                 if column_element.get('name') == 'asignatura_cod':
#                     asignatura_cod = column_element.text
#                 elif column_element.get('name') == 'descripcion':
#                     descripcion = column_element.text
#                 if asignatura_cod is not None and descripcion is not None:
#                     asignatura = {
#                         'codigo': asignatura_cod,
#                         'descripcion': descripcion
#                     }
#                     asignaturas.append(asignatura)

#     # Construir XML manualmente
#     xml_data = '<asignaturas>'
#     for asignatura in asignaturas:
#         xml_data += f'<asignatura><codigo>{asignatura["codigo"]}</codigo><descripcion>{asignatura["descripcion"]}</descripcion></asignatura>'
#     xml_data += '</asignaturas>'

#     # Devolver la respuesta con el contenido XML
#     return HttpResponse(xml_data, content_type='application/xml')