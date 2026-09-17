# django_app/users/views.py
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSignupSerializer, UserMeSerializer

class SignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"id": user.id, "username": user.username, "email": user.email}, 
            status=status.HTTP_201_CREATED
        )

class MeView(generics.RetrieveAPIView):
    serializer_class = UserMeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

# For login, we use SimpleJWT's built-in view but customize response
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # Flatten response to match other frameworks
        if response.status_code == 200:
            return Response({
                "access_token": response.data['access'],
                "token_type": "bearer"
            })
        return response