from ninja import Router
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError

from core.jwt import create_access_token, create_refresh_token, decode_token
from core.auth import JWTAuth

router = Router()
User = get_user_model()


# ======================
# REGISTER
# ======================
@router.post("/register")
def register(request, username: str, password: str, role: str):
    try:
        user = User.objects.create(
            username=username,
            password=make_password(password),
            role=role
        )
        return {"message": "User created"}
    
    except IntegrityError:
        return {"error": "Username already exists"}


# ======================
# LOGIN
# ======================
@router.post("/login")
def login(request, username: str, password: str):

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return {"error": "User not found"}

    if not check_password(password, user.password):
        return {"error": "Wrong password"}

    return {
        "access": create_access_token({"user_id": user.id}),
        "refresh": create_refresh_token({"user_id": user.id}),
    }


# ======================
# REFRESH
# ======================
@router.post("/refresh")
def refresh(request, refresh_token: str):
    payload = decode_token(refresh_token)

    return {
        "access": create_access_token({"user_id": payload["user_id"]})
    }


# ======================
# ME
# ======================
@router.get("/me", auth=JWTAuth())
def me(request):

    user = request.auth

    if not user:
        return {"error": "Unauthorized"}

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role
    }


# ======================
# UPDATE PROFILE (WAJIB BUAT NILAI)
# ======================
@router.put("/me", auth=JWTAuth())
def update_me(request, username: str = None):

    user = request.auth

    if not user:
        return {"error": "Unauthorized"}

    if username:
        user.username = username

    user.save()

    return {"message": "updated"}