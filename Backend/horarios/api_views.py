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
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User

    
#FUNCIONALIDAD PARA SUBIR EL ARCHIVO XML:
class ArchivoUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if 'archivo' not in request.FILES:
            return Response("No se ha enviado ningún archivo.", status=status.HTTP_400_BAD_REQUEST)

        archivo_serializer = ArchivoSerializer(data=request.data)
        if archivo_serializer.is_valid():
            try:
                archivo_instance = archivo_serializer.save()
                
                print(f"Archivo instance: {archivo_instance}")
                
                archivo_instance.archivo = request.FILES['archivo']
                archivo_instance.save()
                
                file_path = archivo_instance.archivo.path
                print(file_path)
                print(f"Archivo guardado en: {file_path}")

                response = cargar_xml(self.request._request, archivo_instance.archivo.path)


                return response

            except Exception as e:
                print(f"Error al guardar el archivo: {e}")
                return Response(f"Error al guardar el archivo: {e}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            print(archivo_serializer.errors)
            return Response(archivo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#XML:
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def cargar_xml(request, file_path):
    try:
        # Leer el archivo XML
        tree = ET.parse(file_path)
        root = tree.getroot()

        print(f"Root element: {root.tag}")

        # Procesar datos de asignaturas
        for table in root.findall(".//table[@name='asignaturas']"):
            print("Encontrada tabla de asignaturas")
            asignatura_data = {}
            for column in table.findall('column'):
                asignatura_data[column.get('name')] = column.text

            asignatura_cod = asignatura_data.get('asignatura_cod')
            descripcion = asignatura_data.get('descripcion')

            print(f"Procesando asignatura: asignatura_cod={asignatura_cod}, descripcion={descripcion}")

            asignatura, created = Asignatura.objects.update_or_create(
                asignatura_cod=asignatura_cod,
                defaults={'descripcion': descripcion}
            )
            if created:
                print(f"Asignatura creada: {asignatura}")
            else:
                print(f"Asignatura actualizada: {asignatura}")

        # Procesar datos de aulas
        for table in root.findall(".//table[@name='aulas']"):
            print("Encontrada tabla de aulas")
            aula_data = {}
            for column in table.findall('column'):
                aula_data[column.get('name')] = column.text

            aula_cod = aula_data.get('aula_cod')
            descripcion = aula_data.get('descripcion')

            # Crear o actualizar el objeto Aula
            Aula.objects.update_or_create(
                aula_cod=aula_cod,
                defaults={'descripcion': descripcion}
            )

        # Procesar datos de franjas
        for table in root.findall(".//table[@name='franjas']"):
            for column in table.findall('column'):
                franja_data = {column.get('name'): column.text for column in table.findall('column')}
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
            for column in table.findall('column'):
                grupo_data = {column.get('name'): column.text for column in table.findall('column')}
                Grupo.objects.update_or_create(
                    grupo_cod=grupo_data.get('grupo_cod'),
                    defaults={'descripcion': grupo_data.get('descripcion')}
                )

        # Procesar datos de profesores
        for table in root.findall(".//table[@name='profesores']"):
            print("Encontrada tabla de profesores")
            profesor_data = {}
            for column in table.findall('column'):
                profesor_data[column.get('name')] = column.text

            profesor_cod = profesor_data.get('professor_cod')
            nombre = profesor_data.get('nombre')

            # Verificar si profesor_cod es None o vacío
            if not profesor_cod:
                print(f"Error: El campo 'profesor_cod' está vacío o no existe.")
                continue

            # Asignar valores predeterminados para los campos que no están en el XML
            email = f"{profesor_cod.lower()}@example.com"  # Email predeterminado

            # Crear el usuario asociado si no existe
            usuario, created = Usuario.objects.get_or_create(username=profesor_cod, defaults={
                'password': Usuario.objects.make_random_password(),
                'rol': Usuario.PROFESOR
            })

            if created:
                print(f"Usuario creado: {usuario}")
            else:
                print(f"Usuario actualizado: {usuario}")

            # Crear o actualizar el objeto Profesor
            profesor, created = Profesor.objects.update_or_create(
                profesor_cod=profesor_cod,
                defaults={
                    'nombre': nombre,
                    'email': email,
                    'usuario': usuario
                }
            )
            if created:
                print(f"Profesor creado: {profesor}")
            else:
                print(f"Profesor actualizado: {profesor}")

        # Procesar datos de horarios
        for table in root.findall(".//table[@name='horarios']"):
            horario_data = {column.get('name'): column.text for column in table.findall('column')}

            # Verificar y manejar si aula_cod está vacío
            aula_cod = horario_data.get('aula_cod')
            if not aula_cod:
                print(f"El campo 'aula_cod' está vacío para el horario con código {horario_data.get('horario_cod')}. Se asignará una cadena vacía.")
                aula_cod = ""  # Asignar una cadena vacía si aula_cod está vacío

            try:
                profesor = Profesor.objects.get(profesor_cod=horario_data.get('professor_cod'))
                asignatura = Asignatura.objects.get(asignatura_cod=horario_data.get('asignatura_cod'))
                grupo = Grupo.objects.get(grupo_cod=horario_data.get('grupo_cod'))
                franja = Franja.objects.get(franja_cod=horario_data.get('franja_cod'))

                # Si aula_cod es una cadena vacía, crear un aula predeterminada
                if aula_cod == "":
                    aula, created = Aula.objects.get_or_create(
                        aula_cod="",
                        defaults={'descripcion': 'Aula no especificada'}
                    )
                else:
                    aula = Aula.objects.get(aula_cod=aula_cod)

                Horario.objects.update_or_create(
                    horario_cod=horario_data.get('horario_cod'),
                    defaults={
                        'profesor_cod': profesor,
                        'dia': horario_data.get('dia'),
                        'asignatura_cod': asignatura,
                        'aula_cod': aula,
                        'grupo_cod': grupo,
                        'franja_cod': franja,
                        'periodo_cod': horario_data.get('periodo_cod')
                    }
                )
            except (Profesor.DoesNotExist, Asignatura.DoesNotExist, Aula.DoesNotExist, Grupo.DoesNotExist, Franja.DoesNotExist) as e:
                print(f"Error: {e}. El horario con código {horario_data.get('horario_cod')} no se puede crear o actualizar.")
                continue

        return Response("Datos cargados exitosamente.", status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error al cargar los datos: {str(e)}")
        return Response(f"Error al cargar los datos: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def borrar_archivoXML(request):
    try:
        # Eliminar todos los registros de las tablas correspondientes
        Horario.objects.all().delete()
        Asignatura.objects.all().delete()
        Aula.objects.all().delete()
        Franja.objects.all().delete()
        Grupo.objects.all().delete()
        Profesor.objects.all().delete()
        Usuario.objects.all().delete()
        
        # Eliminar registros de Asistencia
        Ausencia.objects.all().delete()

        return Response("Base de datos vaciada exitosamente.", status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error al vaciar la base de datos: {str(e)}")
        return Response(f"Error al vaciar la base de datos: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Procesar datos de ausencias
        # for table in root.findall(".//table[@name='ausencias']"):
        #     for column in table.findall('column'):
        #         ausencia_data = {column.get('name'): column.text for column in table.findall('column')}
        #         try:
        #             profesor = Profesor.objects.get(profesor_cod=ausencia_data.get('professor_cod'))
        #             asignatura = Asignatura.objects.get(asignatura_cod=ausencia_data.get('asignatura_cod'))
        #             horario = Horario.objects.get(horario_cod=ausencia_data.get('horario_cod'))

        #             Ausencia.objects.update_or_create(
        #                 profesor_cod=profesor,
        #                 asignatura_cod=asignatura,
        #                 horario_cod=horario,
        #                 defaults={
        #                     'fecha': ausencia_data.get('fecha') or timezone.now(),
        #                     'motivo': ausencia_data.get('motivo')
        #                 }
        #             )
        #         except (Profesor.DoesNotExist, Asignatura.DoesNotExist, Horario.DoesNotExist) as e:
        #             print(f"Error: {e}. La ausencia no se puede crear o actualizar.")
        #             continue



#CRUD HORARIO: 
@api_view(['POST'])
def crear_horario(request):
    serializer = HorarioSerializerCreate(data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response({"message": "Horario Creado"}, status=status.HTTP_201_CREATED)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_horario(request, pk):
    horario = Horario.objects.get(horario_cod=pk)
    serializer = HorarioSerializer(horario)
    return Response(serializer.data)



@api_view(['PUT'])
def update_horario(request, pk):
    try:
        horario = Horario.objects.get(pk=pk)
    except Horario.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = HorarioSerializer(horario, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_horario(request, pk):
    try:
        horario = Horario.objects.get(pk=pk)
    except Horario.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    horario.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['DELETE'])
def eliminar_ausencia(request, id):
    ausencia = Ausencia.objects.get(franja_cod=id)
    try:
        ausencia.delete()
        return Response('Ausencia eliminada')
    except Exception as error:
        return Response(repr(error), status = status.HTTP_500_INTERNAL_SERVER_ERROR)  
       
    

@api_view(['GET'])
def horarios_list(request):
    horarios = Horario.objects.all()
    serializer = HorarioSerializer(horarios,many=True)
    return Response(serializer.data)


#CRUD PARA ASIGNATURAS:
@api_view(['GET'])
def asignaturas_list(request):
    asignaturas = Asignatura.objects.all()
    serializer= AsignaturaSerializer(asignaturas, many=True)
    return Response(serializer.data)
     
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
    
    
#CRUD PROFESORES:  
@api_view(['GET'])
def profesores_obtener(request,id):
    asignatura = Profesor.objects.get(profesor_cod=id)
    serializer= ProfesorSerializer(asignatura)
    return Response(serializer.data)
    
@api_view(['GET'])
def profesores_list(request):
    profesor = Profesor.objects.all()
    serializer = ProfesorSerializer(profesor, many=True)
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
    

    
#CRUD AUSENCIA:
@api_view(['DELETE'])
def eliminar_ausencia(request, id):
    ausencia = Ausencia.objects.get(franja_cod=id)
    try:
        ausencia.delete()
        return Response('Ausencia eliminada')
    except Exception as error:
        return Response(repr(error), status = status.HTTP_500_INTERNAL_SERVER_ERROR)  
    
     



 
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
    
     


""" F U N C I O N A L I D A D E S"""
#Filtrar horarios por profesor:

@api_view(['GET'])
def horario_profesor(request, id):
    try:
        profesor = Profesor.objects.get(profesor_cod=id)
        horarios = Horario.objects.filter(profesor_cod=profesor)
        horario_serializado = HorarioSerializer(horarios, many=True)
        return Response(horario_serializado.data)
    except Profesor.DoesNotExist:
        return Response(f"El profesor con el ID {id} no existe.", status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(f"Error al obtener los horarios del profesor: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Filtrar horario por grupos:
@api_view(['GET'])
def horario_grupo(request, id):
    try:
        grupo = Grupo.objects.get(grupo_cod=id)
        horarios = Horario.objects.filter(grupo_cod=grupo)
        
        # Serializar los datos de los horarios
        horarios_serializados = HorarioSerializer(horarios, many=True).data
        
        # Extraer solo los campos específicos
        horarios_simplificados = [
            {
                'dia': horario['dia'],
                'franja': horario['franja_cod']['descripcion'],  # Utiliza la descripción de la franja horaria
                'asignatura': horario['asignatura_cod']['descripcion']  # Utiliza la descripción de la asignatura
            }
            for horario in horarios_serializados
        ]
        
        return Response(horarios_simplificados, status=status.HTTP_200_OK)
    except Grupo.DoesNotExist:
        return Response({"detail": f"El grupo con el ID {id} no existe."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": f"Error al obtener los horarios del grupo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        














































# # Procesar datos de ausencias
# for table in root.findall(".//table[@name='ausencias']"):
#     for column in table.findall('column'):
#         ausencia_data = {column.get('name'): column.text for column in table.findall('column')}
#         # Procesa los datos de ausencias y guárdalos en el modelo Asistencia
#         # Puedes adaptar esta lógica según la estructura de tus datos de ausencias y tu modelo Asistencia
#         # Por ejemplo:
#         fecha = ausencia_data.get('fecha')
#         motivo = ausencia_data.get('motivo')
#         alumno_cod = ausencia_data.get('alumno_cod')

#         # Aquí deberías guardar los datos de ausencias en tu modelo Asistencia
#         # Por ejemplo:
#         Asistencia.objects.create(fecha=fecha, motivo=motivo, alumno_cod=alumno_cod)
@api_view(['POST'])
def vaciar_base_de_datos(request):
    try:
        # Eliminar todos los registros de las tablas correspondientes
        Horario.objects.all().delete()
        Asignatura.objects.all().delete()
        Aula.objects.all().delete()
        Franja.objects.all().delete()
        Grupo.objects.all().delete()
        Profesor.objects.all().delete()
        Usuario.objects.all().delete()
        
        # Eliminar registros de Asistencia
        Ausencia.objects.all().delete()

        # Eliminar archivos
        archivos = Archivo.objects.all()
        for archivo in archivos:
            archivo_path = os.path.join(settings.MEDIA_ROOT, archivo.archivo.name)
            if os.path.exists(archivo_path):
                os.remove(archivo_path)
            archivo.delete()

        return Response("Base de datos vaciada exitosamente.", status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error al vaciar la base de datos: {str(e)}")
        return Response(f"Error al vaciar la base de datos: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)