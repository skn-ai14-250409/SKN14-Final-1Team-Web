from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("uauth/", include("uauth.urls")),
    path("main/", include("main.urls")),  
    path("mypage/", include("mypage.urls")),
    # ✅ catch-all 위에 둠
]

# 개발 환경에서 정적/미디어 서빙
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 모든 미정의 경로 → 메인으로 리다이렉트 (맨 마지막)
urlpatterns += [
    re_path(r"^.*$", RedirectView.as_view(url="/", permanent=False)),
]
