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
        
        
    def validate_asignatura_cod(self, asignatura_cod):
        asignaturaCode = Asignatura.objects(asignatura_cod=asignatura_cod).first()
        if(not asignaturaCode is None):
            if(not self.instance is None and asignaturaCode.asignatura_cod == self.instance.asignatura_cod):
                pass
            else:
                raise serializers.ValidationError('Ya existe una asignatura con ese código.')
            
        return asignatura_cod
    
    
    def validate_descripcion(self,descripcion):
        if len(descripcion) < 2:
             raise serializers.ValidationError('Al menos debes indicar 2 caracteres')
        return descripcion
    
    
    def create(self, validated_data):
        asignatura = Asignatura.objects.create(
            asignatura_cod = validated_data['asignatura_cod'],
            descripcion = validated_data['descripcion']
        )
        return asignatura
    
    
    def update(self, instance, validated_data):
        instance.asignatura_cod = validated_data['asignatura_cod']
        instance.descripcion = validated_data['descripcion']
        return instance
    
    