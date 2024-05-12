from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
#from .forms import *




@api_view(['GET'])
def profesores_list(request):
   profesores = Profesor.objects.all()
   serializer = ProfesorSerializer(profesores, many=True)
   return Response(serializer.data)