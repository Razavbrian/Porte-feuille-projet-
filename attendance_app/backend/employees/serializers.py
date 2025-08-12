from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'firstname', 'matricule', 'position', 'departement', 'qr_code']
    def create(self, validated_data):
        # Stocker l'employé avec les données du QR code
        return Employee.objects.create(**validated_data)