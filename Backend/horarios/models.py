from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    ADMINISTRADOR = 1
    PROFESOR = 2
    ROLES = (
        (ADMINISTRADOR, 'administrador'),
        (PROFESOR, 'profesor'),
    )
  
    rol = models.PositiveSmallIntegerField(choices=ROLES, default=1)
   

class Asignatura(models.Model):
   asignatura_cod = models.CharField(max_length=50, primary_key=True)
   descripcion = models.CharField(max_length=100)

   def __str__(self):
       return self.asignatura_cod
  


class Aula(models.Model):
   aula_cod = models.CharField(max_length=50, primary_key=True)
   descripcion = models.CharField(max_length=100)


   def __str__(self):
       return self.aula_cod


class Franja(models.Model):
   franja_cod = models.CharField(max_length=50, primary_key=True)
   descripcion = models.CharField(max_length=100)
   horadesde = models.TimeField()
   horahasta = models.TimeField()


   def __str__(self):
       return self.descripcion


class Grupo(models.Model):
   grupo_cod = models.CharField(max_length=50, primary_key=True)
   descripcion = models.CharField(max_length=100)


   def __str__(self):
       return self.grupo_cod

class Profesor(models.Model):
   usuario = models.OneToOneField(Usuario,
                            on_delete = models.CASCADE)
   profesor_cod = models.CharField(max_length=50,primary_key=True)
   nombre = models.CharField(max_length=100)
   email = models.EmailField(max_length=50,blank=True)


   def __str__(self):
       return self.nombre

class Horario(models.Model):
    DIAS = (
        ('L', 'Lunes'),
        ('M', 'Martes'),
        ('X', 'Miércoles'),
        ('J', 'Jueves'),
        ('V', 'Viernes'),
        ('S', 'Sábado'),
        ('D', 'Domingo'),
    )

    horario_cod = models.CharField(max_length=50, primary_key=True)
    profesor_cod = models.ForeignKey('Profesor', on_delete=models.CASCADE)
    dia = models.CharField(max_length=1, choices=DIAS)
    asignatura_cod = models.ForeignKey('Asignatura', on_delete=models.CASCADE)
    aula_cod = models.ForeignKey('Aula', on_delete=models.CASCADE)
    franja_cod = models.ForeignKey('Franja', on_delete=models.CASCADE)
    grupo_cod = models.ForeignKey('Grupo', on_delete=models.CASCADE)
    periodo_cod = models.IntegerField()


    def __str__(self):
       return f"{self.asignatura_cod} - {self.dia} - {self.grupo_cod} - {self.franja_cod}"



class Ausencia(models.Model):
   profesor_cod = models.ForeignKey(Profesor, on_delete=models.CASCADE)
   fecha = models.DateTimeField(default=timezone.now, blank=True)
   motivo = models.TextField(default=True)

   def __str__(self):
       return f"Ausencia de {self.profesor_cod.nombre} el {self.fecha}"


class Archivo(models.Model):
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='archivos/xml/')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre