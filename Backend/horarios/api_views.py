from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import FileResponse, HttpResponse
from .serializers import *
import xml.etree.ElementTree as ET
from django.conf import settings
import os
from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
#from .forms import *


@api_view(['GET'])
def horarios_list(request):
    horarios = Horario.objects.all()
    serializer = HorarioSerializer(horarios,many=True)
    return Response(serializer.data)



@api_view(['GET'])
def grupos_list(request):
    grupos = Grupo.objects.all()
    serializer = GrupoSerializer(grupos, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def franjas_list(request):
    franjas = Franja.objects.all()
    serializer = FranjaSerializer(franjas,many=True)
    return Response(serializer.data)


def xml_data_view(request):
    xml_file_path = os.path.join(settings.BASE_DIR, 'datos.xml')
    
    return FileResponse(open(xml_file_path, 'rb'))

#CRUD PARA ASIGNATURAS:
@api_view(['GET'])
def asignaturas_list(request):
    asignaturas = Asignatura.objects.all()
    serializer= AsignaturaSerializer(asignaturas, many=True)
    return Response(serializer.data)
# @api_view(['GET'])
# def asignaturas_list(request):
#     try:
#         # Parsear el archivo XML
#         tree = ET.parse(settings.XML_FILE_PATH)
#         root = tree.getroot()

#         # Obtener los datos de la tabla de asignaturas del archivo XML
#         asignaturas_data = []
#         for table in root.findall(".//table[@name='asignaturas']"):
#             asignatura_data = {}
#             for column in table.findall('column'):
#                 asignatura_data[column.get('name')] = column.text
#             asignaturas_data.append(asignatura_data)

#         # Guardar las asignaturas en la base de datos
#         for asignatura_data in asignaturas_data:
#             # Intentar obtener la asignatura existente por su código
#             asignatura, created = Asignatura.objects.update_or_create(
#                 asignatura_cod=asignatura_data.get('asignatura_cod'),
#                 defaults={'descripcion': asignatura_data.get('descripcion')}
#             )
        
#         # Serializar las asignaturas para devolverlas como respuesta
#         serializer = AsignaturaSerializer(Asignatura.objects.all(), many=True)

#         # Devolver los datos serializados
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     except FileNotFoundError:
#         return Response("El archivo XML no se encontró.", status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
@api_view(['GET'])
def asignaturas_obtener(request,asignatura_cod):
    asignatura = Asignatura.objects.get(asignatura_cod=asignatura_cod)
    serializer= AsignaturaSerializer(asignatura)
    return Response(serializer.data)

@api_view(['POST'])
def crear_asignatura(request):
    print(request.data)
    serializer = AsignaturaSerializerCreate(data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response("ASIGNATURA CREADA", status=status.HTTP_200_OK)
        except serializers.ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print(repr(error))
            return Response(repr(error), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['PUT'])
# def editar_asignatura(request, asignatura_cod):
#     asignatura = Asignatura.objects.get(asignatura_cod=asignatura_cod)
#     #data["asignatura_cod"] = asignatura_cod
#     asignaturaCreateSerializer = AsignaturaSerializerCreate(data=request.data, instance=asignatura)
#     if asignaturaCreateSerializer.is_valid():
#         try:
#             asignaturaCreateSerializer.save()
#             return Response("Asignatura EDITADA")
#         except serializers.ValidationError as error:
#             return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as error:
#             return Response(repr(error), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     else:
#         return Response(asignaturaCreateSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT'])
def editar_asignatura(request, id):
    try:
        asignatura = Asignatura.objects.get(asignatura_cod=id)
    except Asignatura.DoesNotExist:
        return Response({"error": "Asignatura no encontrada."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = AsignaturaSerializerCreate(asignatura)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = AsignaturaSerializerCreate(asignatura, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response("Asignatura actualizada.", status=status.HTTP_200_OK)
            except Exception as error:
                return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def eliminar_asignatura(request, id):
    asignatura = Asignatura.objects.get(asignatura_cod=id)
    try:
        asignatura.delete()
        return Response('Asignatura Eliminada')
    except Exception as error:
        return Response(repr(error), status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    

    
@api_view(['GET'])
def profesores_obtener(request,id):
    asignatura = Profesor.objects.get(profesor_cod=id)
    serializer= ProfesorSerializer(asignatura)
    return Response(serializer.data)
    


@api_view(['DELETE'])
def eliminar_profesor(request, id):
    profesor = Profesor.objects.get(profesor_cod=id)
    try:
        profesor.delete()
        return Response('Profesor eliminado.')
    except Exception as error:
        return Response(repr(error), status = status.HTTP_500_INTERNAL_SERVER_ERROR)
#CRUD AULA:
@api_view(['GET'])
def aulas_list(request):
   aulas = Aula.objects.all()
   serializer= AulaSerializer(aulas, many=True)
   return Response(serializer.data)


@api_view(['POST'])
def crear_aula(request):
    serializer = AulaSerializerCreate(data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response("Aula creada.")
        except Exception as error:
            return Response(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['PUT'])
def actualizar_aula(request, pk):
    try:
        aula = Aula.objects.get(pk=pk)
    except Aula.DoesNotExist:
        return Response({"error": "Aula no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    serializer = AulaSerializerCreate(aula, data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response("Aula actualizada.", status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
    
    
    
@api_view(['DELETE'])
def eliminar_aula(request, id):
    aula = Aula.objects.get(aula_cod=id)
    try:
        aula.delete()
        return Response('Aula eliminada')
    except Exception as error:
        return Response(repr(error), status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    


#CRUD GRUPOS:
@api_view(['GET'])
def grupos_list(request):
    grupos = Grupo.objects.all()
    serializer = GrupoSerializer(grupos, many=True)
    return Response(serializer.data)




@api_view(['DELETE'])
def eliminar_grupo(request, id):
    grupo = Grupo.objects.get(grupo_cod=id)
    try:
        grupo.delete()
        return Response('Grupo eliminado-')
    except Exception as error:
        return Response(repr(error), status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
#CRUD FRANJAS:
@api_view(['DELETE'])
def eliminar_franja(request, id):
    franja = Franja.objects.get(franja_cod=id)
    try:
        franja.delete()
        return Response('Franja eliminado-')
    except Exception as error:
        return Response(repr(error), status = status.HTTP_500_INTERNAL_SERVER_ERROR)  
    
# @api_view(['GET'])
# def grupos_list(request):
#     try:
#         # Parsear el archivo XML
#         tree = ET.parse(settings.XML_FILE_PATH)
#         root = tree.getroot()

#         # Obtener los datos de la tabla de grupos del archivo XML
#         grupos_data = []
#         for table in root.findall(".//table[@name='grupos']"):
#             grupo_data = {}
#             for column in table.findall('column'):
#                 grupo_data[column.get('name')] = column.text
#             grupos_data.append(grupo_data)
        

#         # Guardar los grupos en la base de datos
#         for grupo_data in grupos_data:
#             grupo, created = Grupo.objects.update_or_create(
#                 grupo_cod=grupo_data.get('grupo_cod'),
#                 defaults={'descripcion': grupo_data.get('descripcion')}
#             )

#         serializer = GrupoSerializer(Grupo.objects.all(),many=True)
        

#         # Devolver los datos serializados
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     except FileNotFoundError:
#         return Response("El archivo XML no se encontró.", status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         logger.error(f"Error: {str(e)}")
#         return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 
#CRUD PROFESORES:
@api_view(['GET'])
def profesores_list(request):
   profesores = Profesor.objects.all()
   serializer = ProfesorSerializer(profesores, many=True)
   return Response(serializer.data)


@api_view(['GET'])
def obtener_profesor(request,id):
    profesor = Profesor.objects.select_related('usuario')
    profesor = profesor.get(profesor_cod=id)
    
    

@api_view(['POST'])
def crear_profesor(request):
    pass

@api_view(['DELETE'])
def eliminar_profesor(request, id):
    profesor = Profesor.objects.get(franja_cod=id)
    try:
        profesor.delete()
        return Response('Profesor eliminado-')
    except Exception as error:
        return Response(repr(error), status = status.HTTP_500_INTERNAL_SERVER_ERROR)  
    
#CRUD AUSENCIA:
@api_view(['DELETE'])
def eliminar_ausencia(request, id):
    ausencia = Ausencia.objects.get(franja_cod=id)
    try:
        ausencia.delete()
        return Response('Ausencia eliminada')
    except Exception as error:
        return Response(repr(error), status = status.HTTP_500_INTERNAL_SERVER_ERROR)  
    
     


# @api_view(['GET'])
# def profesores_list(request):
#     try:
#         # Parsear el archivo XML
#         tree = ET.parse(settings.XML_FILE_PATH)
#         root = tree.getroot()

#         # Obtener los datos de la tabla de profesores del archivo XML
#         profesores_data = []
#         for table in root.findall(".//table[@name='profesores']"):
#             profesor_data = {}
#             for column in table.findall('column'):
#                 profesor_data[column.get('name')] = column.text
#             profesores_data.append(profesor_data)

#         # Guardar los profesores en la base de datos si no existen
#         for profesor_data in profesores_data:
#             profesor, created = Profesor.objects.update_or_create(
#                 profesor_cod = profesor_data.get('profesor_cod'),
#                 defaults ={'nombre': profesor_data.get('nombre')}
#             )
#         # Serializar los profesores para devolverlos como respuesta
#         serializer = ProfesorSerializer(Profesor.objects.all(), many=True)

#         # Devolver los datos serializados
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     except FileNotFoundError:
#         return Response("El archivo XML no se encontró.", status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         print('error:', {e})
#         logger.error(f"Error: {str(e)}")
#         return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def horarios_list(request):
    try:
        # Parsear el archivo XML
        tree = ET.parse(settings.XML_FILE_PATH)
        root = tree.getroot()

        # Obtener los datos de la tabla de horarios del archivo XML
        horarios_data = []
        for table in root.findall(".//table[@name='horarios']"):
            horario_data = {}
            for column in table.findall('column'):
                horario_data[column.get('name')] = column.text
            horarios_data.append(horario_data)

        # Guardar los horarios en la base de datos si no existen
        for horario_data in horarios_data:
            try:
                profesor = Profesor.objects.get(profesor_cod=horario_data.get('profesor_cod'))
                asignatura = Asignatura.objects.get(asignatura_cod=horario_data.get('asignatura_cod'))
                aula = Aula.objects.get(aula_cod=horario_data.get('aula_cod'))
                grupo = Grupo.objects.get(grupo_cod=horario_data.get('grupo_cod'))

                horario, created = Horario.objects.update_or_create(
                    horario_cod=horario_data.get('horario_cod'),
                    defaults={
                        'profesor_cod': profesor,
                        'dia': horario_data.get('dia'),
                        'asignatura_cod': asignatura,
                        'aula_cod': aula,
                        'grupo_cod': grupo,
                        'periodo_cod': horario_data.get('periodo_cod')
                    }
                )
            except (Profesor.DoesNotExist, Asignatura.DoesNotExist, Aula.DoesNotExist, Grupo.DoesNotExist) as e:
                print(f"Error: {e}. El horario con código {horario_data.get('horario_cod')} no se puede crear o actualizar.")
                continue

        # Serializar los horarios para devolverlos como respuesta
        serializer = HorarioSerializer(Horario.objects.all(), many=True)

        # Devolver los datos serializados
        return Response(serializer.data, status=status.HTTP_200_OK)
    except FileNotFoundError:
        return Response("El archivo XML no se encontró.", status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print('error:', {e})
        logger.error(f"Error: {str(e)}")
        return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)





from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser






@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def cargar_xml(request):
    try:
        # Verificar si se ha enviado un archivo
        if 'file' not in request.FILES:
            return Response("No se ha enviado ningún archivo.", status=status.HTTP_400_BAD_REQUEST)

        # Leer el archivo XML
        xml_file = request.FILES['file']
        tree = ET.parse(settings.XML_FILE_PATH)
        root = tree.getroot()

        # Procesar datos de profesores
        for table in root.findall(".//table[@name='profesores']"):
            for row in table.findall('row'):
                profesor_data = {column.get('name'): column.text for column in row.findall('column')}
                Profesor.objects.update_or_create(
                    profesor_cod=profesor_data.get('profesor_cod'),
                    defaults={'nombre': profesor_data.get('nombre')}
                )

        # Procesar datos de asignaturas
        for table in root.findall(".//table[@name='asignaturas']"):
            for row in table.findall('row'):
                asignatura_data = {column.get('name'): column.text for column in row.findall('column')}
                Asignatura.objects.update_or_create(
                    asignatura_cod=asignatura_data.get('asignatura_cod'),
                    defaults={'descripcion': asignatura_data.get('descripcion')}
                )

        # Procesar datos de aulas
        for table in root.findall(".//table[@name='aulas']"):
            for row in table.findall('row'):
                aula_data = {column.get('name'): column.text for column in row.findall('column')}
                Aula.objects.update_or_create(
                    aula_cod=aula_data.get('aula_cod'),
                    defaults={'descripcion': aula_data.get('descripcion')}
                )

        # Procesar datos de franjas
        for table in root.findall(".//table[@name='franjas']"):
            for row in table.findall('row'):
                franja_data = {column.get('name'): column.text for column in row.findall('column')}
                Franja.objects.update_or_create(
                    franja_cod=franja_data.get('franja_cod'),
                    defaults={
                        'descripcion': franja_data.get('descripcion'),
                        'horadesde': franja_data.get('horadesde'),
                        'horahasta': franja_data.get('horahasta')
                    }
                )

        # Procesar datos de grupos
        for table in root.findall(".//table[@name='grupos']"):
            for row in table.findall('row'):
                grupo_data = {column.get('name'): column.text for column in row.findall('column')}
                Grupo.objects.update_or_create(
                    grupo_cod=grupo_data.get('grupo_cod'),
                    defaults={'descripcion': grupo_data.get('descripcion')}
                )

        # Procesar datos de horarios
        for table in root.findall(".//table[@name='horarios']"):
            for row in table.findall('row'):
                horario_data = {column.get('name'): column.text for column in row.findall('column')}
                try:
                    profesor = Profesor.objects.get(profesor_cod=horario_data.get('profesor_cod'))
                    asignatura = Asignatura.objects.get(asignatura_cod=horario_data.get('asignatura_cod'))
                    aula = Aula.objects.get(aula_cod=horario_data.get('aula_cod'))
                    grupo = Grupo.objects.get(grupo_cod=horario_data.get('grupo_cod'))

                    Horario.objects.update_or_create(
                        horario_cod=horario_data.get('horario_cod'),
                        defaults={
                            'profesor_cod': profesor,
                            'dia': horario_data.get('dia'),
                            'asignatura_cod': asignatura,
                            'aula_cod': aula,
                            'grupo_cod': grupo,
                            'periodo_cod': horario_data.get('periodo_cod')
                        }
                    )
                except (Profesor.DoesNotExist, Asignatura.DoesNotExist, Aula.DoesNotExist, Grupo.DoesNotExist) as e:
                    print(f"Error: {e}. El horario con código {horario_data.get('horario_cod')} no se puede crear o actualizar.")
                    continue

        # Procesar datos de ausencias
        for table in root.findall(".//table[@name='ausencias']"):
            for row in table.findall('row'):
                ausencia_data = {column.get('name'): column.text for column in row.findall('column')}
                try:
                    profesor = Profesor.objects.get(profesor_cod=ausencia_data.get('profesor_cod'))
                    asignatura = Asignatura.objects.get(asignatura_cod=ausencia_data.get('asignatura_cod'))
                    horario = Horario.objects.get(horario_cod=ausencia_data.get('horario_cod'))

                    Ausencia.objects.update_or_create(
                        profesor_cod=profesor,
                        asignatura_cod=asignatura,
                        horario_cod=horario,
                        defaults={
                            'fecha': ausencia_data.get('fecha') or timezone.now(),
                            'motivo': ausencia_data.get('motivo')
                        }
                    )
                except (Profesor.DoesNotExist, Asignatura.DoesNotExist, Horario.DoesNotExist) as e:
                    print(f"Error: {e}. La ausencia no se puede crear o actualizar.")
                    continue

        return Response("Datos cargados exitosamente.", status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error al cargar los datos: {str(e)}")
        return Response(f"Error al cargar los datos: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)












#CARGAR ARCHIVO:
class ArchivoUploadView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        archivo_serializer = ArchivoSerializer(data=request.data)

        if archivo_serializer.is_valid():
            archivo_serializer.save()
            cargar_xml()
            return Response(archivo_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(archivo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

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