from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('apps.user.urls')),
    path('api/recipe/', include('apps.recipe.urls')),
    path('docs/schema/', SpectacularAPIView.as_view(), name='docs'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='docs'), name='swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
