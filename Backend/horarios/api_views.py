from pyexpat.errors import messages
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
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils.timezone import make_aware
from django.core.mail import EmailMessage
from django.http import JsonResponse
import base64

    
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
                'password': make_password('iespsur'),
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



"""    

    HORARIOS

"""
@api_view(['GET'])
def horarios_list(request):
    horarios = Horario.objects.all()
    serializer = HorarioSerializer(horarios,many=True)
    return Response(serializer.data)


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


api_view(['DELETE'])
def eliminar_horario(request, pk):
    print(f"Intentando eliminar horario con id: {pk}")
    try:
        # Intentamos convertir a entero si es necesario y manejamos la excepción si falla
        try:
            id = int(id)
        except ValueError:
            pass  # Si falla, continuamos con id como str

        horario = Horario.objects.get(horario_cod=pk)
        print(f"Horario encontrado: {horario}")
        horario.delete()
        print(f"Horario eliminado.")
        return Response({'message': 'Horario eliminado.'}, status=status.HTTP_200_OK)
    except Horario.DoesNotExist:
        print(f"Horario con id {id} no encontrado.")
        return Response({'error': 'Horario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)



"""
    
ASIGNATURAS
    
"""
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
    
""" 
PROFESORES
""" 
@api_view(['GET'])
def profesores_obtener(request,id):
    asignatura = Profesor.objects.get(profesor_cod=id)
    serializer= ProfesorSerializer(asignatura)
    return Response(serializer.data)
    
@api_view(['GET'])
def profesores_list(request):
    profesor = Profesor.objects.all()
    serializer = ProfesorSerializer(profesor, many=True)
    pagination_class = None
    return Response(serializer.data)

@api_view(['DELETE'])
def eliminar_profesor(request, id):
    profesor = Profesor.objects.get(profesor_cod=id)
    try:
        profesor.delete()
        return Response('Profesor eliminado.')
    except Exception as error:
        return Response(repr(error), status = status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtener_profesor(request, profesor_cod):
    try:
        profesor = Profesor.objects.get(profesor_cod=profesor_cod)
        serializer = ProfesorSerializer(profesor)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Profesor.DoesNotExist:
        return Response({"error": "Profesor no encontrado."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def crear_profesor(request):
    serializer = ProfesorSerializerCreate(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Profesor creado exitosamente."}, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def editar_profesor(request, id):
    try:
        profesor = Profesor.objects.get(profesor_cod=id)
    except Profesor.DoesNotExist:
        return Response({"error": "Profesor no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProfesorSerializerCreate(profesor, data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response("Profesor actualizado exitosamente.", status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def eliminar_profesor(request, profesor_cod):
    try:
        profesor = Profesor.objects.get(profesor_cod=profesor_cod)
        profesor.delete()
        return Response("Profesor eliminado exitosamente.", status=status.HTTP_200_OK)
    except Profesor.DoesNotExist:
        return Response({"error": "Profesor no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as error:
        return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


"""
    
AULA

"""
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
    


"""
GRUPOS

"""
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
    
""" 
FRANJAS 

"""
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

@api_view(['DELETE'])
def eliminar_franja(request, id):
    franja = Franja.objects.get(franja_cod=id)
    try:
        franja.delete()
        return Response('Franja eliminado-')
    except Exception as error:
        return Response(repr(error), status = status.HTTP_500_INTERNAL_SERVER_ERROR)  
    
def xml_data_view(request):
    xml_file_path = os.path.join(settings.BASE_DIR, 'datos.xml')
    
    return FileResponse(open(xml_file_path, 'rb'))

"""

    CRUD AULAS:

"""
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

    

"""
    
CRUD AUSENCIAS:

"""
    
@api_view(['GET'])
def obtener_ausencia(request, id):
    try:
        ausencia = Ausencia.objects.get(id=id)
        serializer = AusenciaSerializer(ausencia)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Ausencia.DoesNotExist:
        return Response({"error": "Ausencia no encontrada."}, status=status.HTTP_404_NOT_FOUND)

from django.utils.dateparse import parse_datetime
from datetime import timedelta


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_asignaturas(request):
    try:
        print("Obteniendo profesor...")
        profesor = Profesor.objects.get(usuario=request.user)
        print(f"Profesor encontrado: {profesor}")
        
        fecha_str = request.query_params.get('fecha')
        print(f"Fecha recibida: {fecha_str}")
        
        if not fecha_str:
            print("Falta el parámetro de fecha.")
            return Response({"error": "Falta el parámetro de fecha."}, status=status.HTTP_400_BAD_REQUEST)
        
        fecha = parse_datetime(fecha_str)
        print(f"Fecha parseada: {fecha}")
        
        if not fecha:
            print("Fecha inválida.")
            return Response({"error": "Fecha inválida."}, status=status.HTTP_400_BAD_REQUEST)
        
        dia_semana = fecha.strftime('%A')
        print(f"Día de la semana: {dia_semana}")
        
        dias = {
            'Monday': 'L',
            'Tuesday': 'M',
            'Wednesday': 'X',
            'Thursday': 'J',
            'Friday': 'V',
            'Saturday': 'S',
            'Sunday': 'D'
        }
        dia_semana = dias.get(dia_semana)
        if not dia_semana:
            print("Día de la semana inválido.")
            return Response({"error": "Día de la semana inválido."}, status=status.HTTP_400_BAD_REQUEST)
        
        print("Buscando horarios...")
        horarios = Horario.objects.filter(profesor_cod=profesor, dia=dia_semana)
        print(f"Horarios encontrados: {horarios}")
        
        asignaturas = [{"id": horario.horario_cod, "asignatura": horario.asignatura_cod.descripcion, "franja": horario.franja_cod.descripcion} for horario in horarios]
        
        print(f"Asignaturas encontradas: {asignaturas}")
        return Response(asignaturas, status=status.HTTP_200_OK)
    except Profesor.DoesNotExist:
        print("Profesor no encontrado.")
        return Response({"error": "Profesor no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_ausencia(request):
    try:
        print("Datos recibidos:", request.data)
        usuario = request.user
        profesor_cod = request.data.get('profesor_cod')
        
        if usuario.is_staff:
            if not profesor_cod:
                return Response({"error": "Falta el código del profesor."}, status=status.HTTP_400_BAD_REQUEST)
            profesor = Profesor.objects.get(profesor_cod=profesor_cod)
        else:
            profesor = Profesor.objects.get(usuario=usuario)
        
        print("Profesor encontrado:", profesor)
        
        fecha_str = request.data.get('fecha')
        motivo = request.data.get('motivo')
        horario_id = request.data.get('horario_id')
        dia_entero = request.data.get('dia_entero', False)
        
        if not fecha_str or not motivo:
            print("Campos obligatorios faltantes.")
            return Response({"error": "Faltan campos obligatorios."}, status=status.HTTP_400_BAD_REQUEST)
        
        fecha = parse_datetime(fecha_str)
        if not fecha:
            print("Fecha inválida:", fecha_str)
            return Response({"error": "Fecha inválida."}, status=status.HTTP_400_BAD_REQUEST)
        
        if fecha.tzinfo is not None:
            fecha = fecha.replace(tzinfo=None)
        
        fecha = make_aware(fecha)
        
        if fecha < timezone.now():
            return Response({"error": "No se puede crear una ausencia en una fecha pasada."}, status=status.HTTP_400_BAD_REQUEST)
        
        if Ausencia.objects.filter(profesor_cod=profesor, fecha__date=fecha.date()).exists():
            return Response({"error": "Ya existe una ausencia para el profesor en esta fecha."}, status=status.HTTP_400_BAD_REQUEST)
        
        print("Fecha procesada:", fecha)
        
        if dia_entero:
            print("Creando ausencia para todo el día.")
            ausencia = Ausencia(profesor_cod=profesor, fecha=fecha, motivo=motivo)
            ausencia.save()
            print("Ausencia creada:", ausencia)
        else:
            print("Creando ausencia para una asignatura específica.")
            if not horario_id:
                return Response({"error": "Falta el identificador del horario."}, status=status.HTTP_400_BAD_REQUEST)
            horario = Horario.objects.get(horario_cod=horario_id)
            print('Horario:', horario)
            ausencia = Ausencia(profesor_cod=profesor, fecha=fecha, motivo=motivo)
            print('ausencia:', ausencia)
            ausencia.save()
            print("Ausencia creada:", ausencia)
        
        return Response({
            "message": "Ausencia creada exitosamente.",
            "profesor": profesor.nombre,
            "asignatura": horario.asignatura_cod.descripcion if not dia_entero else "Todo el día",
            "franja": horario.franja_cod.descripcion if not dia_entero else "Todo el día"
        }, status=status.HTTP_201_CREATED)
    except Profesor.DoesNotExist:
        print("Profesor no encontrado.")
        return Response({"error": "Profesor no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Horario.DoesNotExist:
        print("Horario no encontrado.")
        return Response({"error": "Horario no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("Error inesperado:", str(e))
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


  
@api_view(['PUT'])
def editar_ausencia(request, id):
    try:
        ausencia = Ausencia.objects.get(id=id)
    except Ausencia.DoesNotExist:
        return Response({"error": "Ausencia no encontrada."}, status=status.HTTP_404_NOT_FOUND)

    serializer = AusenciaSerializerCreate(ausencia, data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response("Ausencia actualizada exitosamente.", status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def eliminar_ausencia(request, id):
    try:
        ausencia = Ausencia.objects.get(id=id)
        ausencia.delete()
        return Response("Ausencia eliminada exitosamente.", status=status.HTTP_200_OK)
    except Ausencia.DoesNotExist:
        return Response({"error": "Ausencia no encontrada."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as error:
        return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['DELETE'])
def eliminar_ausencia(request, id):
    ausencia = Ausencia.objects.get(franja_cod=id)
    try:
        ausencia.delete()
        return Response('Ausencia eliminada')
    except Exception as error:
        return Response(repr(error), status = status.HTTP_500_INTERNAL_SERVER_ERROR)  
    
""" 
     
     USUARIOS
     
"""
@api_view(['GET'])
def usuarios_list(request):
    usuarios = Usuario.objects.all()
    serializer = UsuarioSerializer(usuarios, many=True)
    return Response(serializer.data)











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
        

from django.utils.dateparse import parse_date
#Obtener guardias:
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_guardias_dia(request):
    try:
        # Obtener el parámetro de fecha
        fecha_str = request.query_params.get('fecha')
        print(f"Fecha recibida: {fecha_str}")
        
        if not fecha_str:
            print("Falta el parámetro de fecha.")
            return Response({"error": "Falta el parámetro de fecha."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Parsear la fecha
        fecha = parse_date(fecha_str)
        if not fecha:
            print("Fecha inválida.")
            return Response({"error": "Fecha inválida."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener el día de la semana (1 = Monday, 7 = Sunday)
        dia_semana = fecha.strftime('%A')
        print(f"Día de la semana: {dia_semana}")

        dias = {
            'Monday': 'L',
            'Tuesday': 'M',
            'Wednesday': 'X',
            'Thursday': 'J',
            'Friday': 'V',
            'Saturday': 'S',
            'Sunday': 'D'
        }
        dia_semana = dias.get(dia_semana)

        if not dia_semana:
            print("Día de la semana inválido.")
            return Response({"error": "Día de la semana inválido."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener los horarios que tienen guardia en la asignatura
        guardias = Horario.objects.filter(dia=dia_semana, asignatura_cod__descripcion__icontains='Guardia')
        print(f"Guardias encontradas: {guardias}")
        
        # Formatear los resultados
        resultado = [
            {
                "profesor": horario.profesor_cod.nombre,
                "asignatura": horario.asignatura_cod.descripcion,
                "aula": horario.aula_cod.descripcion,
                "franja": f"{horario.franja_cod.horadesde} - {horario.franja_cod.horahasta}"
            }
            for horario in guardias
        ]
        
        print(f"Resultado: {resultado}")
        return Response(resultado, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def obtener_ausencias(request):
#     try:
#         fecha_str = request.query_params.get('fecha')
#         if not fecha_str:
#             return Response({"error": "Falta el parámetro de fecha."}, status=status.HTTP_400_BAD_REQUEST)
        
#         fecha = parse_date(fecha_str)
#         if not fecha:
#             return Response({"error": "Fecha inválida."}, status=status.HTTP_400_BAD_REQUEST)
        
#         ausencias = Ausencia.objects.filter(fecha__date=fecha)
#         ausencias_data = [
#             {
#                 "profesor": ausencia.profesor_cod.nombre,
#                 "fecha": ausencia.fecha,
#                 "motivo": ausencia.motivo,
#             }
#             for ausencia in ausencias
#         ]
#         return Response(ausencias_data, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_ausencias(request):
    try:
        print("Inicio de la función obtener_ausencias.")
        
        fecha_str = request.query_params.get('fecha')
        if not fecha_str:
            print("Falta el parámetro de fecha.")
            return Response({"error": "Falta el parámetro de fecha."}, status=status.HTTP_400_BAD_REQUEST)
        
        fecha = parse_date(fecha_str)
        if not fecha:
            print("Fecha inválida.")
            return Response({"error": "Fecha inválida."}, status=status.HTTP_400_BAD_REQUEST)

        print(f"Fecha recibida: {fecha_str}, Fecha parseada: {fecha}")

        ausencias = Ausencia.objects.filter(fecha__date=fecha)
        ausencias_data = []
        
        print(f"Ausencias encontradas para la fecha {fecha}: {len(ausencias)}")

        dias_semana = {
            'Monday': 'L',
            'Tuesday': 'M',
            'Wednesday': 'X',
            'Thursday': 'J',
            'Friday': 'V',
            'Saturday': 'S',
            'Sunday': 'D'
        }

        for ausencia in ausencias:
            print(f"Procesando ausencia: {ausencia}")
            dia_semana = dias_semana.get(ausencia.fecha.strftime('%A'), None)
            if dia_semana is None:
                print(f"Error: Día de la semana {ausencia.fecha.strftime('%A')} no encontrado en el mapa de días.")
                continue

            horarios = Horario.objects.filter(profesor_cod=ausencia.profesor_cod, dia=dia_semana)
            print('Horarios:', horarios)
            print(f"Horarios encontrados para el profesor {ausencia.profesor_cod} en el día {dia_semana}: {len(horarios)}")
            
            for horario in horarios:
                ausencias_data.append({
                    "profesor": ausencia.profesor_cod.nombre,
                    "fecha": ausencia.fecha,
                    "motivo": ausencia.motivo,
                    "asignatura": horario.asignatura_cod.descripcion
                })
                print(f"Asignatura agregada: {horario.asignatura_cod.descripcion}")

        print("Datos de ausencias procesados:", ausencias_data)
        return Response(ausencias_data, status=status.HTTP_200_OK)
    except Exception as e:
        print("Error inesperado:", str(e))
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
   
#Enviar correo
@api_view(['POST'])
def enviar_pdf(request):
    try:
        email = request.data.get('email')
        print(email)
        pdf_base64 = request.data.get('pdf')
        print(pdf_base64)
        if not email or not pdf_base64:
            return Response({"error": "Email y PDF son requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        pdf_bytes = base64.b64decode(pdf_base64)
        
        email_message = EmailMessage(
            subject='Reporte de Guardias y Ausencias',
            body='Adjunto encontrarás el reporte de guardias y ausencias.',
            from_email='your-email@gmail.com',
            to=[email]
        )
        email_message.attach('reporte.pdf', pdf_bytes, 'application/pdf')
        email_message.send()

        return Response({"message": "Correo enviado exitosamente."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




#REGISTRAR USUARIO:
@api_view(['POST'])
def registrar_usuario(request):
    print("Datos recibidos:", request.data)  # Agregar esta línea para imprimir los datos recibidos
    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Usuario registrado exitosamente."}, status=status.HTTP_201_CREATED)
    print("Errores de validación:", serializer.errors)  # Agregar esta línea para imprimir errores de validación
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






#OBTENCIÓN DEL TOKEN:
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Añade datos adicionales al token
        token['username'] = user.username
        token['rol'] = user.rol  # Añade el rol del usuario al token
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'username': self.user.username,
            'rol': self.user.rol,
        }
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_info_usuario(request):
    user = request.user
    return Response({
        "username": user.username,
        #"email": user.email,
        "rol": user.rol,
    })




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