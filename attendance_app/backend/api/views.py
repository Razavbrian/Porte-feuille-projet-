from django.shortcuts import render

# Create your views here.
# api/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        User = get_user_model()  # Récupérer le modèle utilisateur personnalisé
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return Response({"message": "Connexion réussie"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Mot de passe incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

