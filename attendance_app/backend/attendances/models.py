from django.db import models
from employees.models import Employee
# Create your models here.
class Attendance(models.Model):
    TYPE_CHOICES = [
        ('entrée', 'Entrée'),
        ('sortie', 'Sortie'),
    ]
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return f'{self.employee.name} - {self.date}'