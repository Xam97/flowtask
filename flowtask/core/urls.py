# Incluye URLs de cada aplicación modular

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Autenticación y usuarios
    path('', include('users.urls')),
    
    # Tableros y boards
    path('boards/', include('boards.urls')),

    # Comentarios en tareas
    path('comments/', include('comments.urls')),
    
    # Notificaciones
    path('notifications/', include('notifications.urls')),
    
    # Actividad reciente
    path('activity/', include('activity.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)