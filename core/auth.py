from ninja.security import HttpBearer
from django.contrib.auth import get_user_model
from .jwt import decode_token

User = get_user_model()

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        payload = decode_token(token)

        if payload is None:
            print("❌ PAYLOAD NONE")
            return None

        try:
            user = User.objects.get(id=payload["user_id"])
            print("✅ USER:", user)
            return user
        except User.DoesNotExist:
            print("❌ USER NOT FOUND")
            return None