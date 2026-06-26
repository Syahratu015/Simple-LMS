import jwt
from datetime import datetime, timedelta
from django.conf import settings
from ninja.security import HttpBearer
from django.contrib.auth.hashers import make_password, check_password
from .models import User
from functools import wraps
from ninja import Router, Schema

auth_router = Router()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


# ========================
# SCHEMAS
# ========================
class RegisterSchema(Schema):
    username: str
    password: str
    role: str = "student"


class LoginSchema(Schema):
    username: str
    password: str


# ========================
# TOKEN
# ========================
def create_access_token(user: User):
    payload = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        return None


def get_current_user(token: str):
    payload = decode_token(token)
    if not payload:
        return None

    try:
        return User.objects.get(id=payload["user_id"])
    except User.DoesNotExist:
        return None


# ========================
# JWT AUTH
# ========================
class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        return get_current_user(token)


# ========================
# REGISTER
# ========================
@auth_router.post("/register")
def register(request, data: RegisterSchema):
    if User.objects.filter(username=data.username).exists():
        return {"error": "Username already exists"}

    user = User.objects.create(
        username=data.username,
        password=make_password(data.password),
        role=data.role
    )

    return {"message": "User created", "user_id": user.id}


# ========================
# LOGIN
# ========================
@auth_router.post("/login")
def login(request, data: LoginSchema):
    try:
        user = User.objects.get(username=data.username)
    except User.DoesNotExist:
        return {"error": "Invalid credentials"}

    if not check_password(data.password, user.password):
        return {"error": "Invalid credentials"}

    token = create_access_token(user)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@auth_router.get("/me", auth=JWTAuth())
def get_me(request):
    user = request.auth

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role
    }

class UpdateProfileSchema(Schema):
    username: str = None
    password: str = None


@auth_router.put("/me", auth=JWTAuth())
def update_me(request, data: UpdateProfileSchema):
    user = request.auth

    if data.username:
        user.username = data.username

    if data.password:
        user.password = make_password(data.password)

    user.save()

    return {
        "message": "Profile updated",
        "username": user.username
    }

# ========================
# RBAC FIXED
# ========================
def require_role(roles: list):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, "auth", None)

            if not user:
                return {"error": "Unauthorized"}

            if user.role.lower() not in [r.lower() for r in roles]:
                return {"error": "Forbidden"}

            return func(request, *args, **kwargs)

        return wrapper
    return decorator