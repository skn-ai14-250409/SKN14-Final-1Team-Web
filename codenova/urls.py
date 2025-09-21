from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


# health_check 함수
def health_check(request):
    return HttpResponse("OK", status=200)


urlpatterns = [
    path("health/", health_check),
    path("health", health_check),   # 슬래시 없음
    path("admin/", admin.site.urls),
    path("", include("uauth.urls")),
    path("main/", include("main.urls")),
    path("mypage/", include("mypage.urls")),
    path("api-chat/", include("apichat.urls")),
    path("internal-chat/", include("internal.urls")),
]

# 개발 환경에서 정적/미디어 서빙
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
