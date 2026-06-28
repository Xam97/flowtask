# FlowTask

Sistema moderno de gestión de tareas estilo Kanban desarrollado con Django y funcionalidades en tiempo real. FlowTask permite a los equipos organizar, priorizar y colaborar en proyectos de manera eficiente mediante tableros interactivos, notificaciones en tiempo real y un sistema completo de gestión de tareas.

## Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Objetivo del Sistema](#objetivo-del-sistema)
- [Características Principales](#características-principales)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Arquitectura](#arquitectura)
- [Requisitos Previos](#requisitos-previos)
- [Instalación Paso a Paso](#instalación-paso-a-paso)
- [Configuración del Archivo .env](#configuración-del-archivo-env)
- [Variables de Entorno Requeridas](#variables-de-entorno-requeridas)
- [Ejecución del Proyecto](#ejecución-del-proyecto)
- [Aplicación de Migraciones](#aplicación-de-migraciones)
- [Estructura de Directorios](#estructura-de-directorios)
- [Funcionalidades Implementadas](#funcionalidades-implementadas)
- [Sistema de Roles y Permisos](#sistema-de-roles-y-permisos)
- [Buenas Prácticas Implementadas](#buenas-prácticas-implementadas)
- [Solución de Problemas Comunes (Troubleshooting)](#solución-de-problemas-comunes-troubleshooting)
- [Posibles Mejoras Futuras](#posibles-mejoras-futuras)
- [Autores](#autores)
- [Licencia](#licencia)

## Descripción General

FlowTask es una aplicación web de gestión de tareas basada en el metodología Kanban, diseñada para facilitar la colaboración en equipo y el seguimiento de proyectos. Ofrece una interfaz moderna e intuitiva inspirada en herramientas como Monday.com, con soporte para modo claro y oscuro, notificaciones en tiempo real mediante WebSockets, y un sistema completo de gestión de tableros, listas y tarjetas.

## Obetivo del Sistema

El objetivo principal de FlowTask es proporcionar una solución eficiente y accesible para la gestión de tareas y proyectos, permitiendo a los equipos:

- Organizar el trabajo de manera visual mediante tableros Kanban
- Colaborar en tiempo real con actualizaciones instantáneas
- Mantener un registro histórico de todas las actividades
- Gestionar permisos y roles de manera granular
- Priorizar tareas mediante etiquetas y niveles de urgencia
- Visualizar el progreso mediante calendarios y paneles de métricas

## Características Principales

- **Tableros Kanban Interactivos**: Creación y gestión de tableros con listas y tarjetas arrastrables
- **Colaboración en Tiempo Real**: Actualizaciones instantáneas mediante WebSockets (Django Channels)
- **Sistema de Notificaciones**: Alertas en tiempo real para asignaciones, comentarios y cambios
- **Gestión de Miembros**: Sistema de roles (Administrador, Miembro, Espectador) con permisos granulares
- **Etiquetas y Prioridades**: Clasificación visual de tareas con colores y niveles de urgencia
- **Calendario Integrado**: Visualización de tareas con fechas de vencimiento
- **Panel de Métricas**: Estadísticas y análisis de progreso del proyecto
- **Historial de Actividad**: Registro completo de todas las acciones realizadas
- **Búsqueda Global**: Búsqueda rápida de tableros y tareas
- **Modo Claro/Oscuro**: Interfaz adaptable a las preferencias del usuario
- **Diseño Responsive**: Compatible con dispositivos móviles y de escritorio
- **Validación Robusta de Contraseñas**: Requisitos de seguridad avanzados
- **Zona Horaria Configurable**: Soporte para horarios locales (America/Asuncion por defecto)

## Tecnologías Utilizadas

### Backend
- **Django 5.2**: Framework web de Python para el desarrollo rápido y limpio
- **Django REST Framework 3.15+**: API RESTful para servicios web
- **Django Channels 4.1+**: Soporte para WebSockets y comunicación en tiempo real
- **Daphne 4.1.0**: Servidor ASGI para aplicaciones Django con WebSockets
- **python-decouple 3.8+**: Gestión de configuración mediante variables de entorno
- **django-stronghold 0.4.0**: Protección de vistas para usuarios autenticados
- **django-password-validators 1.0.0**: Validación avanzada de contraseñas
- **argon2-cffi 23.1.0**: Hashing seguro de contraseñas con Argon2

### Frontend
- **Bootstrap 5.3.0**: Framework CSS para diseño responsive
- **Font Awesome 6.4.0**: Iconos vectoriales
- **Google Fonts (Inter)**: Tipografía moderna y legible
- **SortableJS**: Biblioteca para funcionalidad drag-and-drop
- **JavaScript Vanilla**: Lógica del cliente sin dependencias pesadas

### Base de Datos
- **SQLite**: Base de datos por defecto para desarrollo (configurable para PostgreSQL/MySQL en producción)

## Arquitectura

FlowTask sigue una arquitectura modular basada en aplicaciones Django (apps), cada una con una responsabilidad específica:

```
flowtask/
├── core/           # Configuración principal del proyecto (settings, urls, wsgi, asgi)
├── users/          # Gestión de autenticación y perfiles de usuario
├── boards/         # Lógica de tableros, listas, tarjetas y etiquetas
├── notifications/  # Sistema de notificaciones y registro de actividad
├── activity/       # Historial y timeline de actividades
├── websockets/     # Consumidores y rutas para comunicación en tiempo real
├── comments/       # Sistema de comentarios en tarjetas
├── static/         # Archivos estáticos (CSS, JS)
└── templates/      # Plantillas HTML
```

### Flujo de Arquitectura

1. **Capa de Presentación**: Plantillas HTML con Bootstrap y JavaScript para interactividad
2. **Capa de Lógica**: Vistas Django y Serializadores DRF para procesamiento de solicitudes
3. **Capa de Datos**: Modelos Django con SQLite para persistencia
4. **Capa de Tiempo Real**: Django Channels con Daphne para WebSockets
5. **Capa de Seguridad**: Middleware, validadores y hashing Argon2

## Requisitos Previos

Antes de instalar FlowTask, asegúrese de tener instalado en su sistema:

- **Python 3.10 o superior**: [Descargar Python](https://www.python.org/downloads/)
- **pip**: Gestor de paquetes de Python (incluido con Python)
- **Git**: Para clonar el repositorio (opcional)
- **Editor de código**: VS Code, PyCharm, o similar (recomendado)

### Verificación de Requisitos

```bash
# Verificar versión de Python
python --version

# Verificar versión de pip
pip --version
```

## Instalación Paso a Paso

### 1. Clonar el Repositorio

```bash
# Clonar el repositorio (si está disponible en un servicio Git)
git clone <url-del-repositorio>
cd flowtask

# O navegar al directorio del proyecto si ya lo tiene descargado
cd "c:\Users\croda\OneDrive\Documentos\Programación V\flowtask"
```

### 2. Crear y Activar Entorno Virtual

Se recomienda encarecidamente utilizar un entorno virtual para aislar las dependencias del proyecto.

#### En Windows (CMD)

```bash
# Crear entorno virtual
python -m venv flowtask\venv

# Activar entorno virtual
flowtask\venv\Scripts\activate
```

#### En Windows (PowerShell)

```bash
# Crear entorno virtual
python -m venv flowtask\venv

# Activar entorno virtual
flowtask\venv\Scripts\Activate.ps1
```

#### En Linux/macOS

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

**Nota**: El entorno virtual ya existe en el proyecto en `flowtask/venv/`. Puede activarlo directamente siguiendo los pasos anteriores.

### 3. Instalar Dependencias

Una vez activado el entorno virtual, instale las dependencias desde el archivo `requirements.txt`:

```bash
# Asegurarse de estar en el directorio correcto
cd flowtask

# Instalar dependencias
pip install -r requirements.txt
```

El archivo `requirements.txt` contiene las siguientes dependencias:

```
Django==5.2
python-decouple>=3.8
djangorestframework>=3.15.0
channels>=4.1.0
daphne==4.1.0
django-stronghold==0.4.0
django-password-validators==1.0.0
argon2-cffi==23.1.0
```

### 4. Configurar el Archivo .env

El proyecto utiliza variables de entorno para la configuración sensible. Copie el archivo `.env.example` y créelo como `.env`:

```bash
# En el directorio flowtask/
copy .env.example .env
```

Luego, edite el archivo `.env` con sus valores de configuración (ver sección [Configuración del Archivo .env](#configuración-del-archivo-env)).

### 5. Aplicar Migraciones de Base de Datos

Ejecute las migraciones para crear la estructura de la base de datos:

```bash
python manage.py migrate
```

Este comando creará automáticamente el archivo `db.sqlite3` con todas las tablas necesarias.

### 6. Crear Superusuario (Opcional)

Para acceder al panel de administración de Django, cree un superusuario:

```bash
python manage.py createsuperuser
```

Siga las instrucciones para ingresar nombre de usuario, email y contraseña.

### 7. Ejecutar el Servidor de Desarrollo

Inicie el servidor de desarrollo de Django:

```bash
python manage.py runserver
```

El servidor estará disponible en `http://127.0.0.1:8000/`

## Configuración del Archivo .env

El archivo `.env` contiene variables de entorno críticas para el funcionamiento del proyecto. Utilice el archivo `.env.example` como plantilla:

### Archivo .env.example

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

### Configuración Recomendada para Desarrollo

```env
SECRET_KEY=django-insecure-development-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

### Configuración Recomendada para Producción

```env
SECRET_KEY=generar-una-clave-secreta-segura-y-larga
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
```

**Importante**: Nunca comprometa el archivo `.env` en un repositorio público. Incluya `.env` en su archivo `.gitignore`.

## Variables de Entorno Requeridas

| Variable | Descripción | Ejemplo | Requerido |
|----------|-------------|---------|-----------|
| `SECRET_KEY` | Clave secreta de Django para firma criptográfica | `django-insecure-#k$...` | Sí |
| `DEBUG` | Modo de depuración (True/False) | `True` o `False` | Sí |
| `ALLOWED_HOSTS` | Hosts permitidos para el sitio (separados por coma) | `127.0.0.1,localhost` | Sí |

### Generación de SECRET_KEY Seguro

Para producción, genere una clave secreta segura utilizando Python:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copie el resultado y úselo como valor para `SECRET_KEY` en su archivo `.env`.

## Ejecución del Proyecto

### Iniciar Servidor de Desarrollo

```bash
# Activar entorno virtual (si no está activado)
flowtask\venv\Scripts\activate

# Navegar al directorio del proyecto
cd flowtask

# Iniciar servidor
python manage.py runserver
```

### Acceder a la Aplicación

- **Aplicación principal**: http://127.0.0.1:8000/
- **Panel de administración**: http://127.0.0.1:8000/admin/
- **API endpoints**: http://127.0.0.1:8000/api/ (si está configurado)

### Detener el Servidor

Presione `Ctrl + C` en la terminal donde se está ejecutando el servidor.

## Aplicación de Migraciones

Las migraciones de Django se utilizan para sincronizar los modelos con la base de datos.

### Crear Nuevas Migraciones

Cuando realice cambios en los modelos:

```bash
python manage.py makemigrations
```

### Aplicar Migraciones Pendientes

```bash
python manage.py migrate
```

### Ver Estado de Migraciones

```bash
python manage.py showmigrations
```

### Revertir Migraciones (Avanzado)

```bash
# Revertir a una migración específica
python manage.py migrate app_name migration_number

# Ejemplo: revertir la última migración de boards
python manage.py migrate boards 0002
```

## Estructura de Directorios

```
flowtask/
├── .env                          # Variables de entorno (no incluir en Git)
├── .env.example                  # Plantilla de variables de entorno
├── .gitignore                    # Archivos ignorados por Git
├── README.md                     # Documentación del proyecto
├── requirements.txt              # Dependencias de Python
│
├── flowtask/                     # Directorio principal del proyecto
│   ├── manage.py                 # Script de gestión de Django
│   ├── db.sqlite3                # Base de datos SQLite (generada automáticamente)
│   │
│   ├── core/                     # Configuración principal
│   │   ├── __init__.py
│   │   ├── settings.py           # Configuración del proyecto
│   │   ├── urls.py               # URLs principales
│   │   ├── wsgi.py               # Configuración WSGI
│   │   ├── asgi.py               # Configuración ASGI (para WebSockets)
│   │   ├── routing.py            # Rutas de WebSockets
│   │   └── context_processors.py # Contextos globales de plantillas
│   │
│   ├── users/                    # Gestión de usuarios
│   │   ├── __init__.py
│   │   ├── models.py             # Modelos de usuario
│   │   ├── views.py              # Vistas de autenticación
│   │   ├── urls.py               # URLs de usuarios
│   │   ├── forms.py              # Formularios de usuario
│   │   └── admin.py              # Configuración de admin
│   │
│   ├── boards/                   # Lógica de tableros
│   │   ├── __init__.py
│   │   ├── models.py             # Modelos: Board, List, Card, Label
│   │   ├── views.py              # Vistas de tableros
│   │   ├── urls.py               # URLs de tableros
│   │   ├── serializers.py        # Serializadores DRF
│   │   ├── permissions.py        # Permisos personalizados
│   │   ├── validators.py         # Validadores personalizados
│   │   ├── consumers.py          # Consumidores de WebSockets
│   │   ├── forms.py              # Formularios de tableros
│   │   └── migrations/           # Migraciones de base de datos
│   │
│   ├── notifications/            # Sistema de notificaciones
│   │   ├── __init__.py
│   │   ├── models.py             # Modelos: Notification, Activity
│   │   ├── views.py              # Vistas de notificaciones
│   │   └── migrations/           # Migraciones
│   │
│   ├── activity/                 # Historial de actividad
│   │   ├── __init__.py
│   │   ├── models.py             # Modelo de actividad
│   │   ├── views.py              # Vistas de actividad
│   │   └── urls.py               # URLs de actividad
│   │
│   ├── websockets/               # Comunicación en tiempo real
│   │   ├── __init__.py
│   │   ├── consumers.py          # Consumidores de WebSockets
│   │   ├── routing.py            # Rutas de WebSockets
│   │   └── models.py             # Modelos relacionados
│   │
│   ├── comments/                 # Sistema de comentarios
│   │   ├── __init__.py
│   │   ├── models.py             # Modelo de comentarios
│   │   ├── views.py              # Vistas de comentarios
│   │   └── migrations/           # Migraciones
│   │
│   ├── static/                   # Archivos estáticos
│   │   ├── css/
│   │   │   ├── layout.css        # Estilos generales
│   │   │   ├── dashboard.css     # Estilos del dashboard
│   │   │   ├── auth.css          # Estilos de autenticación
│   │   │   ├── boards.css        # Estilos de tableros
│   │   │   └── pages.css         # Estilos de páginas adicionales
│   │   └── js/
│   │       ├── helpers.js        # Utilidades JavaScript
│   │       ├── theme.js          # Gestión de temas
│   │       ├── api.js            # Llamadas a API
│   │       ├── websocket.js      # Conexión WebSocket
│   │       ├── dashboard.js      # Lógica del dashboard
│   │       ├── search.js         # Funcionalidad de búsqueda
│   │       ├── board.js          # Lógica de tableros
│   │       ├── notifications.js  # Gestión de notificaciones
│   │       └── auth.js           # Lógica de autenticación
│   │
│   └── templates/                # Plantillas HTML
│       ├── base.html             # Plantilla base
│       ├── auth/
│       │   ├── login.html        # Página de inicio de sesión
│       │   └── register.html     # Página de registro
│       ├── boards/
│       │   ├── board_detail.html  # Detalle de tablero
│       │   ├── edit_board.html   # Edición de tablero
│       │   ├── edit_card.html    # Edición de tarjeta
│       │   └── edit_list.html    # Edición de lista
│       ├── users/
│       │   ├── profile.html      # Perfil de usuario
│       │   └── preferences.html  # Preferencias de usuario
│       ├── dashboard.html        # Dashboard principal
│       ├── calendar/
│       │   └── calendar.html     # Calendario
│       ├── activity/
│       │   └── activity.html     # Historial de actividad
│       ├── labels/
│       │   └── labels.html       # Gestión de etiquetas
│       ├── panel/
│       │   └── panel.html        # Panel de métricas
│       └── search/
│           └── results.html      # Resultados de búsqueda
```

## Funcionalidades Implementadas

### Gestión de Tableros
- Creación, edición y eliminación de tableros
- Organización de tableros en listas Kanban
- Archivado de tableros
- Gestión de miembros en tableros

### Gestión de Listas y Tarjetas
- Creación de listas personalizadas
- Creación de tarjetas con título, descripción y prioridad
- Arrastrar y soltar (drag-and-drop) para reorganizar
- Asignación de usuarios a tarjetas
- Fechas de vencimiento
- Etiquetado con colores
- Marcado de tarjetas como completadas

### Sistema de Roles y Permisos
- **Administrador**: Control total sobre el tablero
- **Miembro**: Permisos configurables (gestionar etiquetas, eliminar tarjetas, editar listas, invitar miembros)
- **Espectador**: Solo lectura del tablero

### Notificaciones en Tiempo Real
- Alertas para asignaciones de tareas
- Notificaciones de nuevos comentarios
- Alertas de cambios en tarjetas
- Indicador de notificaciones no leídas
- Opción para marcar todas como leídas
- Eliminación de notificaciones leídas

### Calendario
- Visualización mensual de tareas
- Resaltado de tareas vencidas
- Navegación entre meses
- Filtrado por prioridad

### Panel de Métricas
- Estadísticas de tableros
- Distribución de prioridades
- Progreso de listas
- Tareas recientes
- Métricas de productividad

### Búsqueda Global
- Búsqueda de tableros por nombre
- Búsqueda de tarjetas por título y descripción
- Resultados en tiempo real
- Navegación rápida a resultados

### Historial de Actividad
- Registro completo de acciones
- Timeline visual de actividades
- Filtrado por tipo de acción
- Información de usuario y timestamp

### Gestión de Perfil
- Visualización de perfil de usuario
- Estadísticas personales (tableros, tareas creadas, asignadas, completadas)
- Configuración de preferencias (tema claro/oscuro)

### Seguridad
- Validación robusta de contraseñas (mínimo 8 caracteres, no solo números, contiene mayúsculas, minúsculas y caracteres especiales)
- Hashing de contraseñas con Argon2
- Protección CSRF
- Sesiones seguras
- Autenticación requerida para todas las vistas (django-stronghold)

## Sistema de Roles y Permisos

FlowTask implementa un sistema granular de roles y permisos para controlar el acceso a las funcionalidades del tablero.

### Roles Disponibles

#### 1. Administrador (admin)
- **Permisos**: Control total sobre el tablero
- Puede crear, editar y eliminar tableros
- Puede agregar y eliminar miembros
- Puede asignar roles
- Puede gestionar todas las configuraciones del tablero

#### 2. Miembro (member)
- **Permisos**: Permisos configurables según la configuración del tablero
- **Permisos adicionales otorgables**:
  - `can_manage_labels`: Puede crear y editar etiquetas
  - `can_delete_cards`: Puede eliminar tarjetas
  - `can_edit_lists`: Puede crear, editar y eliminar listas
  - `can_invite`: Puede invitar nuevos miembros al tablero

#### 3. Espectador (viewer)
- **Permisos**: Solo lectura
- Puede ver tableros, listas y tarjetas
- No puede realizar modificaciones
- Ideal para stakeholders o clientes que necesitan solo visibilidad

### Implementación Técnica

El sistema de permisos se implementa mediante:

1. **Modelo Membership**: Tabla intermedia entre usuarios y tableros
2. **Permisos Django**: Decoradores y mixins en vistas
3. **Validación en Frontend**: Deshabilitación de elementos según rol
4. **Validación en Backend**: Verificación de permisos antes de ejecutar acciones

### Ejemplo de Uso

```python
# Verificar si un usuario puede eliminar tarjetas
membership = Membership.objects.get(user=request.user, board=board)
if membership.role == 'admin' or membership.can_delete_cards:
    # Permitir eliminación
    pass
else:
    # Denegar acceso
    raise PermissionDenied
```

## Buenas Prácticas Implementadas

### Seguridad
- **Hashing de Contraseñas**: Uso de Argon2, uno de los algoritmos más seguros
- **Validación de Contraseñas**: Requisitos estrictos (longitud, complejidad, no comunes)
- **Protección CSRF**: Habilitado por defecto en Django
- **Variables de Entorno**: Configuración sensible en `.env`, nunca en código
- **Sesiones Seguras**: Cookies HTTPOnly, SameSite=Lax
- **Autenticación Requerida**: Todas las vistas protegidas con django-stronghold

### Código
- **Modularidad**: Separación clara en apps Django con responsabilidades específicas
- **DRY (Don't Repeat Yourself)**: Reutilización de código mediante mixins, utilidades y componentes
- **Nomenclatura Consistente**: Nombres descriptivos en inglés para modelos, vistas y funciones
- **Comentarios**: Documentación en español para modelos y funciones complejas
- **Validación**: Validación en backend y frontend para consistencia

### Base de Datos
- **Migraciones**: Control de versiones del esquema de base de datos
- **Índices**: Campos indexados para optimización de consultas
- **Relaciones**: Uso apropiado de ForeignKey, ManyToMany y relaciones intermedias
- **Constraints**: unique_together para integridad referencial

### Frontend
- **Separación de Responsabilidades**: CSS modular, JavaScript organizado por funcionalidad
- **Responsive Design**: Adaptación a diferentes tamaños de pantalla
- **Accesibilidad**: Uso de etiquetas semánticas y atributos ARIA
- **Performance**: Carga optimizada de recursos, uso de CDN para bibliotecas
- **UX/UI**: Diseño intuitivo inspirado en herramientas líderes del mercado

### Desarrollo
- **Entorno Virtual**: Aislamiento de dependencias del proyecto
- **Requirements.txt**: Gestión explícita de dependencias con versiones fijas
- **Git Ignore**: Exclusión de archivos sensibles y generados
- **Configuración por Entorno**: Diferentes configuraciones para desarrollo y producción

### Arquitectura
- **MVT (Model-View-Template)**: Patrón arquitectónico de Django
- **API REST**: Separación de frontend y backend mediante DRF
- **WebSockets**: Comunicación en tiempo real con Django Channels
- **Middleware**: Interceptación y procesamiento de solicitudes
- **Context Processors**: Datos globales disponibles en todas las plantillas

## Solución de Problemas Comunes (Troubleshooting)

### Problema: Error "ModuleNotFoundError"

**Síntoma**: Al ejecutar comandos de Django, aparece un error de módulo no encontrado.

**Solución**:
```bash
# Asegurarse de que el entorno virtual esté activado
flowtask\venv\Scripts\activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Problema: Error "SECRET_KEY not set"

**Síntoma**: El servidor no inicia con error de clave secreta no configurada.

**Solución**:
```bash
# Copiar archivo .env.example a .env
copy .env.example .env

# Editar .env y establecer un valor para SECRET_KEY
SECRET_KEY=django-insecure-development-key-change-in-production
```

### Problema: Migraciones no aplican correctamente

**Síntoma**: Error al ejecutar `python manage.py migrate`.

**Solución**:
```bash
# Verificar estado de migraciones
python manage.py showmigrations

# Si hay migraciones conflictivas, eliminar la base de datos y volver a crear
del db.sqlite3
python manage.py migrate
```

**Advertencia**: Esto eliminará todos los datos. Úsolo en desarrollo.

### Problema: WebSockets no funcionan

**Síntoma**: Las notificaciones en tiempo real no se actualizan.

**Solución**:
```bash
# Verificar que Daphne esté instalado
pip show daphne

# Asegurarse de que ASGI_APPLICATION esté configurado en settings.py
ASGI_APPLICATION = 'core.asgi.application'

# Reiniciar el servidor
python manage.py runserver
```

### Problema: Error de permisos en producción

**Síntoma**: Error 403 o 500 en producción.

**Solución**:
```bash
# Verificar ALLOWED_HOSTS en .env
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Verificar DEBUG=False
DEBUG=False

# Recopilar archivos estáticos
python manage.py collectstatic
```

### Problema: Contraseñas no cumplen requisitos

**Síntoma**: Error al crear usuario con contraseña "demasiado común" o "demasiado corta".

**Solución**:
- La contraseña debe tener al menos 8 caracteres
- No puede ser completamente numérica
- Debe contener al menos una letra mayúscula
- Debe contener al menos una letra minúscula
- Debe contener al menos un carácter especial
- No puede ser una contraseña común (ej: "password123")

**Ejemplo de contraseña válida**: `MiContraseñaSegura2024!`

### Problema: Error de zona horaria

**Síntoma**: Las fechas se muestran con desfase horario.

**Solución**:
```python
# En settings.py, verificar TIME_ZONE
TIME_ZONE = 'America/Asuncion'
USE_TZ = True
```

### Problema: Estilos CSS no cargan correctamente

**Síntoma**: La página se ve sin estilos.

**Solución**:
```bash
# Verificar que STATIC_URL esté configurado en settings.py
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# En desarrollo, Django sirve archivos estáticos automáticamente
# En producción, usar:
python manage.py collectstatic
```

### Problema: Error "Port already in use"

**Síntoma**: El servidor no inicia porque el puerto 8000 está en uso.

**Solución**:
```bash
# Usar un puerto diferente
python manage.py runserver 8001

# O encontrar y detener el proceso que usa el puerto 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## Posibles Mejoras Futuras

### Funcionalidades
- **Integración con Calendarios Externos**: Google Calendar, Outlook
- **Sistema de Recordatorios**: Notificaciones por email para tareas vencidas
- **Archivos Adjuntos**: Posibilidad de adjuntar archivos a tarjetas
- **Checklists en Tarjetas**: Listas de subtareas dentro de una tarjeta
- **Vistas de Gantt**: Visualización temporal de proyectos
- **Plantillas de Tableros**: Crear tableros a partir de plantillas predefinidas
- **Exportación de Datos**: Exportar tableros a PDF, Excel, CSV
- **API Pública**: Documentación completa de API para integraciones de terceros
- **Webhooks**: Notificaciones a servicios externos ante eventos
- **Sistema de Etiquetas Avanzado**: Etiquetas jerárquicas y categorías

### Tecnológicas
- **Base de Datos en Producción**: Migración a PostgreSQL o MySQL
- **Redis para WebSockets**: Usar Redis como channel layer para producción
- **Caching**: Implementar Redis o Memcached para caché
- **CDN para Archivos Estáticos**: Usar Cloudflare o AWS CloudFront
- **Docker**: Contenedorización del proyecto para despliegue fácil
- **CI/CD**: Pipeline automatizado para pruebas y despliegue
- **Testing**: Suite completa de pruebas unitarias y de integración
- **TypeScript**: Migrar JavaScript a TypeScript para mayor seguridad de tipos
- **Frontend Framework**: Considerar React o Vue.js para SPA más complejo

### UX/UI
- **Modo Offline**: Soporte para trabajar sin conexión
- **Atajos de Teclado**: Navegación rápida mediante keyboard shortcuts
- **Drag-and-drop Mejorado**: Mejorar la experiencia de arrastrar y soltar
- **Animaciones**: Transiciones más suaves y micro-interacciones
- **Tema Personalizable**: Permitir a usuarios crear sus propios temas
- **Accesibilidad**: Mejorar soporte para lectores de pantalla
- **Móvil**: Aplicación móvil nativa (React Native o Flutter)

### Seguridad
- **2FA (Two-Factor Authentication)**: Autenticación de dos factores
- **OAuth2**: Login con Google, GitHub, etc.
- **Audit Logging**: Registro detallado de acciones de seguridad
- **Rate Limiting**: Limitar solicitudes para prevenir abuso
- **CSP (Content Security Policy)**: Política de seguridad de contenido
- **Helmet**: Headers de seguridad HTTP adicionales

### Rendimiento
- **Lazy Loading**: Cargar componentes bajo demanda
- **Virtual Scrolling**: Para listas muy largas
- **Optimización de Imágenes**: Compresión y formatos modernos (WebP)
- **Code Splitting**: Dividir código en chunks más pequeños
- **Service Workers**: Para PWA (Progressive Web App)

## Autores

FlowTask es un proyecto de gestión de tareas desarrollado con Django, diseñado para facilitar la colaboración en equipo y la organización de proyectos.

## Licencia

Este proyecto es de código abierto y está disponible bajo la [Licencia MIT](LICENSE).

---

**Nota**: Este README está diseñado para ser una guía completa para desarrolladores que deseen clonar, configurar y ejecutar el proyecto. Si encuentra algún problema o tiene sugerencias de mejora, por favor abra un issue en el repositorio.
