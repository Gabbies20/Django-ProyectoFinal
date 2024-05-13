from rest_framework import serializers
from . models import *






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
      
class HorarioSerializer(serializers.ModelSerializer):
   class Meta:
       model = Horario
       fields = '__all__'
      
      
class ProfesorSerializer(serializers.ModelSerializer):
   class Meta:
       model = Profesor
       fields = '__all__'
      


class AusenciaSerializer(serializers.ModelSerializer):
   class Meta:
       model = Ausencia
       fileds = '__all__'



#SERIALIZADORES:
class AsignaturaSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Asignatura
        fields = ['asignatura_cod','descripcion']