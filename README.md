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
- [Autores](#autores)
- [Licencia](#licencia)

## Descripción General

FlowTask es una aplicación web para la gestión colaborativa de tareas y proyectos basada en la metodología Kanban, con una experiencia de uso similar a Trello. Permite organizar el trabajo mediante tableros, listas y tarjetas, facilitando la planificación, el seguimiento de actividades y la colaboración en tiempo real a través de notificaciones y WebSockets.

## Objetivo del Sistema

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

- **Python 3.13** (compatible con Python 3.10 o superior): Lenguaje de programación utilizado para el desarrollo del proyecto.
- **Django 5.2**: Framework web principal para el desarrollo de la aplicación.
- **Django REST Framework 3.15+**: Utilizado para la serialización, validación de datos y algunos servicios internos del sistema.
- **Django Channels 4.1+**: Comunicación en tiempo real mediante WebSockets.
- **Daphne 4.1.0**: Servidor ASGI para aplicaciones Django con soporte para WebSockets.
- **python-decouple 3.8+**: Gestión de variables de entorno y configuración sensible.
- **django-stronghold 0.4.0**: Protección de vistas para usuarios autenticados.
- **django-password-validators 1.0.0**: Validación avanzada de contraseñas.
- **argon2-cffi 23.1.0**: Hashing seguro de contraseñas mediante Argon2.

### Frontend
- **Bootstrap 5.3.0**: Framework CSS para diseño responsive
- **Font Awesome 6.4.0**: Iconos vectoriales
- **Google Fonts (Inter)**: Tipografía moderna y legible
- **SortableJS**: Biblioteca para funcionalidad drag-and-drop
- **JavaScript Vanilla**: Lógica del cliente sin dependencias pesadas

### Base de Datos
- **SQLite**: Base de datos por defecto para desarrollo (configurable para PostgreSQL/MySQL en producción)

## Arquitectura

FlowTask está desarrollado siguiendo el patrón arquitectónico **MVT (Model-View-Template)** de Django y una estructura modular basada en aplicaciones (*apps*), donde cada módulo posee una responsabilidad específica.

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
2. **Capa de Lógica**: Vistas Django encargadas de procesar solicitudes, aplicar reglas de negocio y apoyarse en serializadores DRF cuando se requiere validar o transformar datos.
3. **Capa de Datos**: Modelos Django con SQLite para persistencia
4. **Capa de Tiempo Real**: Django Channels con Daphne para WebSockets
5. **Capa de Seguridad**: Middleware, validadores y hashing Argon2

## Requisitos Previos

Antes de instalar FlowTask, asegúrese de tener instalado en su sistema:

- **Python 3.12 o superior (probado con Python 3.13)**: [Descargar Python](https://www.python.org/downloads/)
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
cd flowtask
# O navegar al directorio del proyecto si ya lo tiene descargado

```

### 2. Crear y Activar el Entorno Virtual

Se recomienda utilizar un entorno virtual para aislar las dependencias del proyecto y evitar conflictos con otros entornos de Python.

#### Windows (PowerShell)

```bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
.\venv\Scripts\Activate.ps1
```

#### Windows (CMD)

```bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
venv\Scripts\activate.bat
```

#### Linux/macOS

```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate
```

Una vez activado, la terminal mostrará el prefijo:

```text
(venv)
```

lo que indica que el entorno virtual está listo para instalar las dependencias del proyecto.

### 3. Instalar Dependencias
Una vez activado el entorno virtual, instale las dependencias desde el archivo `requirements.txt`:

```bash
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

### 6. Crear Superusuario (Opcional, solo si desea acceder al panel de administración de Django).

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

## Configuración del Archivo `.env`

FlowTask utiliza variables de entorno para almacenar configuraciones sensibles, como la clave secreta de Django y la configuración del entorno.

Después de clonar el repositorio, copie el archivo `.env.example` y cree un nuevo archivo llamado `.env`.

### Windows

```bash
copy .env.example .env
```

### Linux/macOS

```bash
cp .env.example .env
```

El archivo `.env.example` contiene la configuración básica necesaria para ejecutar el proyecto:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Una vez creado el archivo `.env`, reemplace `your-secret-key` por una clave secreta propia.

> **Importante:** El archivo `.env` contiene información sensible y **no debe incluirse en el repositorio**. Asegúrese de que esté agregado al archivo `.gitignore`.

## Variables de Entorno Requeridas

| Variable | Descripción | Requerida |
|----------|-------------|:---------:|
| `SECRET_KEY` | Clave secreta utilizada por Django para la seguridad de la aplicación. | Sí |
| `DEBUG` | Activa o desactiva el modo de desarrollo. | Sí |
| `ALLOWED_HOSTS` | Lista de hosts permitidos para acceder a la aplicación. | Sí |

### Generar una `SECRET_KEY`

Puede generar una clave secreta segura ejecutando el siguiente comando:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copie el valor generado y reemplácelo en el archivo `.env`.

## Ejecución del Proyecto

### Iniciar Servidor de Desarrollo en PowerShell

```bash
# Activar el entorno virtual
.\venv\Scripts\Activate.ps1

# Iniciar el servidor
python manage.py runserver

```

### Acceder a la Aplicación

- **Aplicación principal**: http://127.0.0.1:8000/
- **Panel de administración**: http://127.0.0.1:8000/admin/

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
│   │   ├── serializers.py        # Serializadores para validación y transformación de datos
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
- Ideal para clientes que necesitan solo visibilidad

### Implementación Técnica

El sistema de permisos se implementa mediante:

1. **Modelo Membership**: Tabla intermedia entre usuarios y tableros
2. **Permisos Django**: Decoradores y mixins en vistas
3. **Validación en Frontend**: Deshabilitación de elementos según rol
4. **Validación en Backend**: Verificación de permisos antes de ejecutar acciones

Los permisos se validan tanto en el frontend como en el backend para garantizar que cada usuario únicamente pueda realizar las acciones autorizadas según su rol dentro del tablero.

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
- **UX/UI**: Interfaz basada en la metodología Kanban, similar a Trello

### Desarrollo
- **Entorno Virtual**: Aislamiento de dependencias del proyecto
- **Requirements.txt**: Gestión explícita de dependencias con versiones fijas
- **Git Ignore**: Exclusión de archivos sensibles y generados
- **Configuración por Entorno**: Diferentes configuraciones para desarrollo y producción

### Arquitectura
- **MVT (Model-View-Template):** Patrón arquitectónico principal utilizado por Django.
- **Aplicaciones Modulares:** Separación del sistema en apps independientes según su responsabilidad.
- **WebSockets:** Comunicación en tiempo real mediante Django Channels.
- **Middleware:** Procesamiento de solicitudes y seguridad.
- **Context Processors:** Datos globales compartidos entre las plantillas.
- **Django REST Framework:** Utilizado para serialización, validación de datos y algunos servicios internos del sistema.

## Solución de Problemas Comunes (Troubleshooting)

### Problema: Error "ModuleNotFoundError"

**Síntoma**: Al ejecutar comandos de Django, aparece un error de módulo no encontrado.

**Solución**:
```bash
# Asegurarse de que el entorno virtual esté activado
.\venv\Scripts\Activate.ps1

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
SECRET_KEY=<tu-clave-generada>
```
Puede generar una nueva clave utilizando el comando mostrado en la sección "Configuración del Archivo .env".

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

**Advertencia**: Esto eliminará todos los datos. Úsalo en desarrollo.

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

## Autores

Proyecto desarrollado como parte de la asignatura **Programación V**.

Desarrollado por:

- Fabián Giménez
- Camila Rodas
- Alan Rojas

---
## Licencia

Este proyecto fue desarrollado con fines académicos como parte de la asignatura **Programación V**.

Puede utilizarse como material de estudio y referencia respetando la autoría correspondiente.

**Nota**: Este README tiene como objetivo facilitar la instalación, configuración y comprensión de la arquitectura del proyecto para fines académicos y de desarrollo.
