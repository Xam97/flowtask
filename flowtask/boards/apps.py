# users/apps.py
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Usuarios y Autenticación'

# boards/apps.py
class BoardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'boards'
    verbose_name = 'Tableros y Tarjetas'

# notifications/apps.py
class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = 'Notificaciones'

# activity/apps.py
class ActivityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'activity'
    verbose_name = 'Actividad Reciente'

# websockets/apps.py
class WebsocketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'websockets'
    verbose_name = 'WebSockets'