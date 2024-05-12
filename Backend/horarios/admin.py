from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Asignatura)
admin.site.register(Aula)
admin.site.register(Franja)
admin.site.register(Grupo)
admin.site.register(Horario)
admin.site.register(Profesor)
admin.site.register(Ausencia)