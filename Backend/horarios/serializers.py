from rest_framework import serializers
from .models import *

class UsuarioSerializer(serializers.ModelSerializer):
   class Meta:
       model = Usuario
       fields = '__all__'

class AsignaturaSerializer(serializers.ModelSerializer):
   class Meta:
       model = Asignatura
       fields = '__all__'

class AulaSerializer(serializers.ModelSerializer):
   class Meta:
       model = Aula
       fields = '__all__'

class FranjaSerializer(serializers.ModelSerializer):
   class Meta:
       model = Franja
       fields = '__all__'

class GrupoSerializer(serializers.ModelSerializer):
   class Meta:
       model = Grupo
       fields = '__all__'

class ProfesorSerializer(serializers.ModelSerializer):
   class Meta:
       model = Profesor
       fields = '__all__'

class ProfesorSerializerMejorado(serializers.ModelSerializer):
    usuario = UsuarioSerializer()
    class Meta:
        model = Profesor
        fields = ('usuario', 'profesor_cod', 'nombre', 'email')

class HorarioSerializer(serializers.ModelSerializer):
    profesor_cod = ProfesorSerializer()
    asignatura_cod = AsignaturaSerializer()
    aula_cod = AulaSerializer()
    franja_cod = FranjaSerializer()
    grupo_cod = GrupoSerializer()
    class Meta:
       model = Horario
       fields = ('horario_cod', 'profesor_cod', 'dia', 'asignatura_cod', 'aula_cod', 'franja_cod', 'grupo_cod', 'periodo_cod')

class HorarioSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Horario
        fields = ('horario_cod', 'profesor_cod', 'dia', 'asignatura_cod', 'aula_cod', 'franja_cod', 'grupo_cod', 'periodo_cod')

    def validate_horario_cod(self, horario_cod):
        if Horario.objects.filter(horario_cod=horario_cod).exists():
            raise serializers.ValidationError('Ya existe un horario con ese código.')
        return horario_cod

    def validate_dia(self, dia):
        if dia not in dict(Horario.DIAS).keys():
            raise serializers.ValidationError('Día no válido. Debe ser una de las siguientes letras: L, M, X, J, V, S, D.')
        return dia

    def validate_periodo_cod(self, periodo_cod):
        if not (1 <= periodo_cod <= 9):
            raise serializers.ValidationError('El periodo debe estar entre 1 y 9.')
        return periodo_cod

class AusenciaSerializer(serializers.ModelSerializer):
   class Meta:
       model = Ausencia
       fields = '__all__'

class AsignaturaSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Asignatura
        fields = ('asignatura_cod', 'descripcion')

    def validate_asignatura_cod(self, asignatura_cod):
        if Asignatura.objects.filter(asignatura_cod=asignatura_cod).exists():
            raise serializers.ValidationError('Ya existe una asignatura con ese código.')
        return asignatura_cod

    def validate_descripcion(self, descripcion):
        if len(descripcion) < 2:
            raise serializers.ValidationError('Al menos debes indicar 2 caracteres')
        return descripcion

class AulaSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Aula
        fields = ('aula_cod', 'descripcion')

    def validate_aula_cod(self, aula_cod):
        if Aula.objects.filter(aula_cod=aula_cod).exists():
            raise serializers.ValidationError('Ya existe un aula con ese código.')
        return aula_cod

    def validate_descripcion(self, descripcion):
        if len(descripcion) < 2:
            raise serializers.ValidationError('Al menos debes indicar 2 caracteres')
        return descripcion

class ArchivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archivo
        fields = '__all__'


class UsuarioSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'rol')

    def create(self, validated_data):
        user = Usuario.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            rol=validated_data['rol']
        )
        return user


    
    
    
        """
            AUSENCIAS
        
        """

class AusenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ausencia
        fields = ['profesor_cod', 'fecha', 'motivo']
        
        
class AusenciaSerializerCreate(serializers.ModelSerializer):

    class Meta:
        model = Ausencia
        fields = ('profesor_cod', 'fecha', 'motivo')

    def validate_profesor_cod(self, profesor_cod):
        if not Profesor.objects.filter(profesor_cod=profesor_cod).exists():
            raise serializers.ValidationError('El profesor especificado no existe.')
        return profesor_cod

    def validate_motivo(self, value):
        if len(value) < 5:
            raise serializers.ValidationError('El motivo debe tener al menos 5 caracteres.')
        return value

    def create(self, validated_data):
        ausencia = Ausencia.objects.create(
            profesor_cod = validated_data['profesor_cod'],
            fecha = validated_data['fecha'],
            motivo = validated_data['motivo']
        )
        return ausencia
    
    
    
""" USUARIOS_PROFESORES"""
   
        
        
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class ProfesorSerializerCreate(serializers.ModelSerializer):
    usuario = UsuarioSerializer()

    class Meta:
        model = Profesor
        fields = ('usuario', 'profesor_cod', 'nombre', 'email')

    def validate_profesor_cod(self, profesor_cod):
        if Profesor.objects.filter(profesor_cod=profesor_cod).exists():
            raise serializers.ValidationError('El código de profesor ya existe.')
        return profesor_cod

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')
        usuario, created = Usuario.objects.get_or_create(**usuario_data)
        profesor = Profesor.objects.create(usuario=usuario, **validated_data)
        return profesor
    

""" REGISTRO """
class UsuarioSerializerRegistro(serializers.Serializer):
 
    username = serializers.CharField()
    password1 = serializers.CharField()
    password2 = serializers.CharField()
    email = serializers.EmailField()
    rol = serializers.IntegerField()
    
    def validate_username(self,username):
        usuario = Usuario.objects.filter(username=username).first()
        if(not usuario is None):
            raise serializers.ValidationError('Ya existe un usuario con ese nombre')
        return username
    
    
    
"""LOGIN"""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if not user.is_active:
            raise serializers.ValidationError('La combinación de credenciales no tiene una cuenta activa')

        return data
    
    

    
#REGISTRO:
class UsuarioSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField()

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'email', 'rol', 'nombre']

    def create(self, validated_data):
        user = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            rol=validated_data['rol']
        )

        # Si el usuario es un profesor, crear una entrada en el modelo Profesor
        if validated_data['rol'] == Usuario.PROFESOR:
            Profesor.objects.create(
                usuario=user,
                profesor_cod=validated_data['username'],
                nombre=validated_data['nombre'],
                email=validated_data['email']
            )

        return user