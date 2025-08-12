from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Employee
from .serializers import EmployeeSerializer
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
# Create your views here.
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def perform_create(self, serializer):
        employee = serializer.save()

        