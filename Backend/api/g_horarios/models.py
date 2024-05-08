from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class Usuario(AbstractUser):
    ADMINISTRADOR = 1
    PROFESOR = 2
    ROLES = (
        (ADMINISTRADOR,'administrador'),
        (PROFESOR,'profesor'),
        )
    
    rol = models.PositiveSmallIntegerField(
        choices = ROLES, default=1
    )
    groups = models.ManyToManyField(Group, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions')

    
    

class Asignatura(models.Model):
    asignatura_cod = models.CharField(max_length=50, primary_key=True)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion

class Aula(models.Model):
    aula_cod = models.CharField(max_length=50, primary_key=True)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion

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
        return self.descripcion

class Horario(models.Model):
    horario_cod = models.CharField(max_length=50, primary_key=True)
    professor_cod = models.CharField(max_length=50)
    dia = models.CharField(max_length=1)
    asignatura_cod = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    aula_cod = models.ForeignKey(Aula, on_delete=models.CASCADE)
    grupo_cod = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    periodo_cod = models.IntegerField()

    def __str__(self):
        return f"{self.asignatura_cod} - {self.dia} - {self.grupo_cod}"

class Profesor(models.Model):
    usuario = models.OneToOneField(Usuario, 
                             on_delete = models.CASCADE)
    profesor_cod = models.CharField(max_length=50, primary_key=True)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=50)
    hash = models.CharField(max_length=8)
    hash2 = models.CharField(max_length=8)

    def __str__(self):
        return self.nombre


class Ausencia(models.Model):
    profesor_cod = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    asignatura_cod = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    horario_cod = models.ForeignKey(Horario, on_delete=models.CASCADE)
    fecha = models.DateField()
    motivo = models.TextField()

    def __str__(self):
        return f"Ausencia de {self.profesor_cod.nombre} en {self.asignatura_cod.descripcion} el {self.fecha}"