from rest_framework.response import Response
from rest_framework.views import APIView
from diller.serializers import EmployeeDetailsSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RegisterView(APIView):
    @swagger_auto_schema(
        request_body=EmployeeDetailsSerializer,
        responses={200: 'Success', 400: 'Bad Request'},
    )
    def post(self, request):
        serializer = EmployeeDetailsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
