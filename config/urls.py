from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from ninja import NinjaAPI

from accounts.api import router as auth_router
from courses.api import router as course_router  
from enroll.api import router as enroll_router


api = NinjaAPI()

api.add_router("/auth/", auth_router)
api.add_router("/courses/", course_router)  
api.add_router("/enroll/", enroll_router)


# ======================
# ROOT ENDPOINT
# ======================
def home(request):
    return JsonResponse({
        "message": "Simple LMS API 🚀",
        "docs": "/api/docs",
        "admin": "/admin",
        "endpoints": [
            "/api/auth/",
            "/api/courses/",
            "/api/enroll/"
        ]
    })


urlpatterns = [
    path('', home),  # 🔥 ini biar gak 404
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]