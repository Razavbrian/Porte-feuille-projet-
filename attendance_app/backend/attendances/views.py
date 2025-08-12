from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Attendance
from .serializers import AttendanceSerializer
from django.utils import timezone

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get("employee_id")
        date = request.data.get("date")

        try:
            # Vérifier si la dernière présence est une entrée sans sortie
            last_attendance = Attendance.objects.filter(employee_id=employee_id).order_by('-date').first()

            if last_attendance and last_attendance.type == "entrée":
                # Marquer une sortie pour cet employé
                serializer = self.get_serializer(data={
                    "employee_id": employee_id,
                    "date": date,
                    "type": "sortie"
                })
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response(serializer.data, status=status.HTTP_200_OK)

            else:
                # Créer une nouvelle entrée de présence
                serializer = self.get_serializer(data={
                    "employee_id": employee_id,
                    "date": date,
                    "type": "entrée"
                })
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
