from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from core.views import CustomUserViewSet

admin.site.site_header = 'ChainStore Admin'
admin.site.index_title = 'Admin'


auth_router = DefaultRouter()
auth_router.register('users', CustomUserViewSet, basename='users')


urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('store/', include('store.urls')),
    path('auth/', include(auth_router.urls)),
    path('auth/', include('djoser.urls.jwt')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
