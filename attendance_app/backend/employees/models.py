from django.db import models

# Create your models here.
class Employee(models.Model):
    name = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    matricule = models.CharField(max_length=20, unique=True)
    position = models.CharField(max_length=100)
    departement = models.CharField(max_length=100)
    qr_code = models.BinaryField()  # Utiliser BinaryField pour stocker les données du QR code  
def __str__(self):
        return self.name