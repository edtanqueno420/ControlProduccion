# ControlProduccion API

API de control de producción y manufactura construida con Django REST Framework.

URL desplegada: [https://tanqueno-produccion.uaeftt-ute.site](https://tanqueno-produccion.uaeftt-ute.site)

## Tecnologías

| Tecnología | Versión |
|---|---|
| Python | >= 3.12 |
| Django | >= 6.0.4 |
| Django REST Framework | >= 3.17.1 |
| Django Filters | >= 25.2 |
| SimpleJWT | >= 5.5.1 |
| PostgreSQL | 16+ |
| django-cors-headers | >= 4.9.0 |
| python-decouple | >= 3.8 |

## Requisitos previos

- Python >= 3.12
- PostgreSQL >= 16
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes)

## Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd ControlProduccion
```

### 2. Crear y activar entorno virtual

```bash
uv venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias

```bash
uv sync
```

### 4. Configurar PostgreSQL

Crear la base de datos:

```bash
sudo -u postgres psql
CREATE DATABASE controlproduccion_db;
CREATE USER postgres WITH PASSWORD 'postgres';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'America/Guayaquil';
GRANT ALL PRIVILEGES ON DATABASE controlproduccion_db TO postgres;
\q
```

### 5. Configurar variables de entorno

Copiar el archivo de ejemplo:

```bash
cp .env.example .env
```

Editar `.env` con tu configuración:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,tanqueno-produccion.uaeftt-ute.site

DB_NAME=controlproduccion_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
TEST_DB_NAME=controlproduccion_test_db

CORS_ALLOW_ALL_ORIGINS=True
```

| Variable | Descripción | Por defecto |
|---|---|---|
| `SECRET_KEY` | Clave secreta de Django (requerida) | — |
| `DEBUG` | Activar modo debug | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos separados por coma | — |
| `DB_NAME` | Nombre de la base de datos PostgreSQL | — |
| `DB_USER` | Usuario de PostgreSQL | — |
| `DB_PASSWORD` | Contraseña de PostgreSQL | — |
| `DB_HOST` | Host de la base de datos | `localhost` |
| `DB_PORT` | Puerto de la base de datos | `5432` |
| `TEST_DB_NAME` | Nombre de la base de datos de pruebas | `controlproduccion_test_db` |
| `CORS_ALLOW_ALL_ORIGINS` | Permitir todos los orígenes CORS | `False` |

### 6. Ejecutar migraciones

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### 7. Crear superusuario

```bash
uv run python manage.py createsuperuser
```

### 8. Iniciar servidor de desarrollo

```bash
uv run python manage.py runserver
```

La API estará disponible en `http://localhost:8000/api/`.

## Estructura del proyecto

```
ControlProduccion/
├── config/                          # Configuración del proyecto Django
│   ├── __init__.py
│   ├── settings.py                  # Configuración (DRF, JWT, BD, CORS)
│   ├── urls.py                      # Configuración de rutas raíz
│   ├── asgi.py                      # Punto de entrada ASGI
│   └── wsgi.py                      # Punto de entrada WSGI
├── manufacturing/                   # Aplicación principal
│   ├── __init__.py
│   ├── admin.py                     # Configuración del admin de Django
│   ├── apps.py                      # AppConfig
│   ├── filters.py                   # FilterSets por recurso
│   ├── models.py                    # Re-export de modelos
│   ├── pagination.py                # Paginación estándar
│   ├── permissions.py               # Permisos personalizados
│   ├── urls.py                      # Router y patrones de URL
│   ├── views.py                     # Placeholder
│   ├── models/
│   │   ├── __init__.py
│   │   ├── profile.py               # Perfil de usuario con rol
│   │   ├── product.py               # Producto (materia prima, producto terminado)
│   │   ├── bom.py                   # Lista de materiales (BOM) + Detalles
│   │   ├── work_center.py           # Centros de trabajo / máquinas
│   │   ├── production_order.py      # Órdenes de producción
│   │   └── inventory_movement.py    # Movimientos de inventario
│   ├── serializers/
│   │   ├── __init__.py
│   │   ├── auth.py                  # Serializer personalizado JWT
│   │   ├── user.py                  # User, Register, Profile, ChangePassword
│   │   ├── product.py               # Serializer de producto
│   │   ├── bom.py                   # Serializers de BOM + Detalle
│   │   ├── work_center.py           # Serializer de centro de trabajo
│   │   ├── production_order.py      # Serializer de orden de producción
│   │   └── inventory_movement.py    # Serializer de movimiento de inventario
│   ├── views/
│   │   ├── __init__.py
│   │   ├── health.py                # Endpoint de health check
│   │   ├── auth.py                  # Register, Logout
│   │   ├── user.py                  # CRUD usuarios + perfil, estadísticas
│   │   ├── product.py               # CRUD productos + reabastecer, estadísticas
│   │   ├── bom.py                   # CRUD BOM + estadísticas
│   │   ├── work_center.py           # CRUD centros de trabajo + estadísticas
│   │   ├── production_order.py      # CRUD órdenes + flujo de trabajo
│   │   └── inventory_movement.py    # Listar movimientos + ajustar
│   └── tests/
│       ├── __init__.py
│       ├── helpers.py               # Fábricas de pruebas
│       ├── test_auth.py
│       ├── test_users.py
│       ├── test_products.py
│       ├── test_bom.py
│       ├── test_work_centers.py
│       ├── test_production_orders.py
│       └── test_inventory_movements.py
├── .env.example                     # Plantilla de variables de entorno
├── .gitignore
├── manage.py                        # Punto de entrada CLI de Django
└── pyproject.toml                   # Metadatos y dependencias del proyecto
```

## Autenticación

La API utiliza **JWT (JSON Web Tokens)** a través de `djangorestframework-simplejwt`. Todos los endpoints excepto health check, registro e inicio de sesión requieren autenticación.

### Configuración JWT

| Configuración | Valor |
|---|---|
| Duración del access token | 60 minutos |
| Duración del refresh token | 1 día |
| Rotar refresh tokens | Sí |
| Bloquear después de rotación | Sí |
| Algoritmo | HS256 |
| Tipo de header de autenticación | Bearer |

## Endpoints de la API

### Health

| Método | Endpoint | Permiso | Descripción |
|---|---|---|---|
| GET | `/api/health/` | AllowAny | Health check del servicio |

### Autenticación

| Método | Endpoint | Permiso | Descripción |
|---|---|---|---|
| POST | `/api/auth/register/` | AllowAny | Registrar nuevo usuario |
| POST | `/api/auth/login/` | AllowAny | Iniciar sesión, devuelve tokens JWT |
| POST | `/api/auth/token/refresh/` | AllowAny | Refrescar access token |
| POST | `/api/auth/token/verify/` | AllowAny | Verificar validez del token |
| POST | `/api/auth/logout/` | IsAuthenticated | Cerrar sesión, bloquea refresh token |

### Usuarios

| Método | Endpoint | Permiso | Descripción |
|---|---|---|---|
| GET | `/api/users/` | IsAdminUser | Listar usuarios |
| POST | `/api/users/` | IsAdminUser | Crear usuario |
| GET | `/api/users/{id}/` | IsAdminUser | Obtener detalle de usuario |
| PUT | `/api/users/{id}/` | IsAdminUser | Actualizar usuario |
| PATCH | `/api/users/{id}/` | IsAdminUser | Actualizar parcialmente usuario |
| DELETE | `/api/users/{id}/` | IsAdminUser | Eliminar usuario |
| GET | `/api/users/profile/` | IsAuthenticated | Obtener perfil propio |
| PATCH | `/api/users/profile/` | IsAuthenticated | Actualizar perfil propio |
| POST | `/api/users/change-password/` | IsAuthenticated | Cambiar contraseña propia |
| POST | `/api/users/{id}/toggle-active/` | IsAdminUser | Activar/desactivar usuario |
| GET | `/api/users/stats/` | IsAdminUser | Estadísticas de usuarios |

**Campos de búsqueda**: `username`, `email`, `first_name`, `last_name`

**Campos de filtro**: `is_staff`, `is_active`

**Campos de ordenamiento**: `id`, `username`, `date_joined`

### Productos

| Método | Endpoint | Permiso | Descripción |
|---|---|---|---|
| GET | `/api/products/` | IsStaffOrReadOnly | Listar productos |
| POST | `/api/products/` | IsStaffOrReadOnly | Crear producto |
| GET | `/api/products/{id}/` | IsStaffOrReadOnly | Obtener detalle de producto |
| PUT | `/api/products/{id}/` | IsStaffOrReadOnly | Actualizar producto |
| PATCH | `/api/products/{id}/` | IsStaffOrReadOnly | Actualizar parcialmente producto |
| DELETE | `/api/products/{id}/` | IsStaffOrReadOnly | Eliminar producto |
| POST | `/api/products/{id}/restock/` | IsAdminUser | Reabastecer producto |
| GET | `/api/products/available/` | AllowAny | Listar productos disponibles (con stock) |
| GET | `/api/products/stats/` | IsAuthenticated | Estadísticas de productos |

**Campos de búsqueda**: `nombre`, `codigo_sku`, `descripcion`

**Campos de filtro**: `tipo`, `activo`, `nombre` (icontains), `stock_min` (gte), `stock_max` (lte)

**Campos de ordenamiento**: `nombre`, `stock_actual`, `created_at`

### Listas de Materiales (BOM)

| Método | Endpoint | Permiso | Descripción |
|---|---|---|---|
| GET | `/api/bill-of-materials/` | IsStaffOrReadOnly | Listar BOMs |
| POST | `/api/bill-of-materials/` | IsStaffOrReadOnly | Crear BOM |
| GET | `/api/bill-of-materials/{id}/` | IsStaffOrReadOnly | Obtener detalle de BOM |
| PUT | `/api/bill-of-materials/{id}/` | IsStaffOrReadOnly | Actualizar BOM |
| PATCH | `/api/bill-of-materials/{id}/` | IsStaffOrReadOnly | Actualizar parcialmente BOM |
| DELETE | `/api/bill-of-materials/{id}/` | IsStaffOrReadOnly | Eliminar BOM |
| GET | `/api/bill-of-materials/stats/` | IsAuthenticated | Estadísticas de BOMs |

**Campos de búsqueda**: `producto_terminado__nombre`, `observaciones`

**Campos de filtro**: `producto_terminado`, `activa`, `version`

**Campos de ordenamiento**: `created_at`, `version`

Los detalles de BOM se gestionan de forma inline a través de los endpoints CRUD de BOM (anidados debajo de cada BOM).

### Centros de Trabajo

| Método | Endpoint | Permiso | Descripción |
|---|---|---|---|
| GET | `/api/work-centers/` | IsStaffOrReadOnly | Listar centros de trabajo |
| POST | `/api/work-centers/` | IsStaffOrReadOnly | Crear centro de trabajo |
| GET | `/api/work-centers/{id}/` | IsStaffOrReadOnly | Obtener detalle de centro de trabajo |
| PUT | `/api/work-centers/{id}/` | IsStaffOrReadOnly | Actualizar centro de trabajo |
| PATCH | `/api/work-centers/{id}/` | IsStaffOrReadOnly | Actualizar parcialmente centro de trabajo |
| DELETE | `/api/work-centers/{id}/` | IsStaffOrReadOnly | Eliminar centro de trabajo |
| GET | `/api/work-centers/stats/` | IsAuthenticated | Estadísticas de centros de trabajo |

**Campos de búsqueda**: `codigo`, `nombre_maquina`, `descripcion`

**Campos de filtro**: `estado`, `activo`

**Campos de ordenamiento**: `codigo`, `capacidad_diaria`

### Órdenes de Producción

| Método | Endpoint | Permiso | Descripción |
|---|---|---|---|
| GET | `/api/production-orders/` | IsOwnerOrStaff | Listar órdenes de producción |
| POST | `/api/production-orders/` | IsOwnerOrStaff | Crear orden de producción |
| GET | `/api/production-orders/{id}/` | IsOwnerOrStaff | Obtener detalle de orden |
| PUT | `/api/production-orders/{id}/` | IsOwnerOrStaff | Actualizar orden |
| PATCH | `/api/production-orders/{id}/` | IsOwnerOrStaff | Actualizar parcialmente orden |
| DELETE | `/api/production-orders/{id}/` | IsOwnerOrStaff | Eliminar orden |
| POST | `/api/production-orders/{id}/start/` | IsAuthenticated | Iniciar producción (valida stock) |
| POST | `/api/production-orders/{id}/complete/` | IsAuthenticated | Completar orden (inventario automático) |
| POST | `/api/production-orders/{id}/pause/` | IsAuthenticated | Pausar producción |
| POST | `/api/production-orders/{id}/cancel/` | IsAuthenticated | Cancelar producción |
| GET | `/api/production-orders/stats/` | IsAdminUser | Estadísticas de órdenes |

**Campos de filtro**: `estado`, `prioridad`, `centro_trabajo`, `producto`, `from_date` (gte), `to_date` (lte)

**Campos de ordenamiento**: `created_at`, `cantidad_a_producir`, `prioridad`

### Movimientos de Inventario

| Método | Endpoint | Permiso | Descripción |
|---|---|---|---|
| GET | `/api/inventory-movements/` | IsAuthenticated | Listar movimientos de inventario |
| GET | `/api/inventory-movements/{id}/` | IsAuthenticated | Obtener detalle de movimiento |
| POST | `/api/inventory-movements/adjust/` | IsAdminUser | Ajuste manual de stock |
| GET | `/api/inventory-movements/stats/` | IsAuthenticated | Estadísticas de movimientos |

**Campos de filtro**: `tipo_movimiento`, `producto`, `orden_produccion`, `from_date` (gte), `to_date` (lte)

**Campos de ordenamiento**: `fecha_movimiento`, `created_at`

## Ejemplos de uso

### Registrar un nuevo usuario

```bash
curl -X POST https://tanqueno-produccion.uaeftt-ute.site/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "operator1",
    "email": "operator1@test.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "role": "OPERARIO"
  }'
```

Respuesta:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs...",
  "user_id": 1,
  "username": "operator1",
  "email": "operator1@test.com",
  "role": "OPERARIO"
}
```

### Iniciar sesión

```bash
curl -X POST https://tanqueno-produccion.uaeftt-ute.site/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "operator1", "password": "SecurePass123!"}'
```

### Usar el access token

```bash
curl https://tanqueno-produccion.uaeftt-ute.site/api/products/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

### Refrescar token

```bash
curl -X POST https://tanqueno-produccion.uaeftt-ute.site/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJhbGciOiJIUzI1NiIs..."}'
```

### Paginación

Todos los endpoints de listado soportan paginación:

```bash
curl "https://tanqueno-produccion.uaeftt-ute.site/api/products/?page=1&page_size=25"
```

| Parámetro | Descripción | Por defecto | Máximo |
|---|---|---|---|
| `page` | Número de página | 1 | — |
| `page_size` | Elementos por página | 10 | 100 |

### Búsqueda

```bash
curl "https://tanqueno-produccion.uaeftt-ute.site/api/products/?search=acero"
```

### Filtrado

```bash
curl "https://tanqueno-produccion.uaeftt-ute.site/api/products/?tipo=RAW_MATERIAL&activo=true"
curl "https://tanqueno-produccion.uaeftt-ute.site/api/production-orders/?estado=IN_PROGRESS&from_date=2026-01-01"
```

### Ordenamiento

```bash
curl "https://tanqueno-produccion.uaeftt-ute.site/api/products/?ordering=-stock_actual"
curl "https://tanqueno-produccion.uaeftt-ute.site/api/production-orders/?ordering=-created_at"
```

## Roles y permisos

### Roles

| Rol | `is_staff` | Descripción |
|---|---|---|
| `ADMIN` | `true` | Acceso completo a todos los endpoints |
| `SUPERVISOR` | `true` | Puede crear/editar recursos, igual que staff |
| `OPERARIO` | `false` | Solo lectura, puede gestionar sus propias órdenes |

### Clases de permiso

| Permiso | Comportamiento |
|---|---|
| `AllowAny` | Sin autenticación requerida (health, register, login) |
| `IsAuthenticated` | Cualquier usuario autenticado |
| `IsAdminUser` | Solo usuarios con `is_staff=True` (ADMIN, SUPERVISOR) |
| `IsStaffOrReadOnly` | Métodos seguros (GET, HEAD, OPTIONS) = cualquier autenticado; mutaciones (POST, PUT, PATCH, DELETE) = solo staff |
| `IsOwnerOrStaff` | A nivel de objeto: propietario (`usuario_responsable`) o staff |

### Matriz de permisos por modelo

| Recurso | Listar/Detalle | Crear | Actualizar | Eliminar | Acciones personalizadas |
|---|---|---|---|---|---|
| Usuarios | Admin | Admin | Admin | Admin | Perfil (Authenticated), Stats (Admin) |
| Productos | StaffOrRead | StaffOrRead | StaffOrRead | StaffOrRead | Restock (Admin), Available (Public) |
| BOMs | StaffOrRead | StaffOrRead | StaffOrRead | StaffOrRead | Stats (Authenticated) |
| Centros Trabajo | StaffOrRead | StaffOrRead | StaffOrRead | StaffOrRead | Stats (Authenticated) |
| Órdenes Prod. | OwnerOrStaff | OwnerOrStaff | OwnerOrStaff | OwnerOrStaff | Start/Pause/Complete/Cancel (Authenticated), Stats (Admin) |
| Mov. Inventario | Authenticated | — | — | — | Adjust (Admin), Stats (Authenticated) |

## Modelos de datos

### Profile

Extiende el modelo `User` de Django con un campo de rol (relación 1 a 1).

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | BigAutoField | Clave primaria |
| `user` | OneToOneField(User) | `on_delete=CASCADE`, `related_name='profile'` |
| `role` | CharField(20) | Opciones: `ADMIN`, `SUPERVISOR`, `OPERARIO`; Por defecto: `OPERARIO` |

### Product

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | BigAutoField | Clave primaria |
| `codigo_sku` | CharField(50) | `unique` |
| `nombre` | CharField(200) | |
| `descripcion` | TextField | `blank=True`, `default=''` |
| `tipo` | CharField(20) | Opciones: `RAW_MATERIAL`, `IN_PROCESS`, `FINISHED_GOOD` |
| `stock_actual` | PositiveIntegerField | `default=0` |
| `unidad_medida` | CharField(20) | `default='units'` |
| `stock_minimo` | PositiveIntegerField | `default=0` |
| `activo` | BooleanField | `default=True` (soft delete) |
| `created_at` | DateTimeField | `auto_now_add` |
| `updated_at` | DateTimeField | `auto_now` |

### BillOfMaterial

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | BigAutoField | Clave primaria |
| `producto_terminado` | ForeignKey(Product) | `on_delete=PROTECT`, `related_name='boms'`, `limit_choices_to={'tipo': 'FINISHED_GOOD'}` |
| `version` | PositiveIntegerField | `default=1` |
| `cantidad_base` | DecimalField(10, 2) | `default=1` |
| `activa` | BooleanField | `default=True` |
| `observaciones` | TextField | `blank=True`, `default=''` |
| `created_at` | DateTimeField | `auto_now_add` |
| `updated_at` | DateTimeField | `auto_now` |

**Restricción única**: (`producto_terminado`, `version`)

### BillOfMaterialDetail

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | BigAutoField | Clave primaria |
| `lista_materiales` | ForeignKey(BillOfMaterial) | `on_delete=CASCADE`, `related_name='detalles'` |
| `materia_prima` | ForeignKey(Product) | `on_delete=PROTECT`, `related_name='bom_details'`, `limit_choices_to={'tipo': 'RAW_MATERIAL'}` |
| `cantidad_requerida` | DecimalField(10, 2) | |
| `desperdicio_porcentaje` | DecimalField(5, 2) | `default=0` |
| `created_at` | DateTimeField | `auto_now_add` |
| `updated_at` | DateTimeField | `auto_now` |

### WorkCenter

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | BigAutoField | Clave primaria |
| `codigo` | CharField(50) | `unique` |
| `nombre_maquina` | CharField(200) | |
| `descripcion` | TextField | `blank=True`, `default=''` |
| `estado` | CharField(20) | Opciones: `ACTIVE`, `MAINTENANCE`, `INACTIVE`; Por defecto: `ACTIVE` |
| `capacidad_diaria` | PositiveIntegerField | `default=1` |
| `activo` | BooleanField | `default=True` |
| `created_at` | DateTimeField | `auto_now_add` |
| `updated_at` | DateTimeField | `auto_now` |

### ProductionOrder

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | BigAutoField | Clave primaria |
| `codigo_orden` | CharField(50) | `unique` |
| `producto` | ForeignKey(Product) | `on_delete=PROTECT`, `related_name='production_orders'` |
| `cantidad_a_producir` | PositiveIntegerField | |
| `cantidad_producida` | PositiveIntegerField | `default=0` |
| `fecha_inicio` | DateTimeField | `null=True`, `blank=True` |
| `fecha_fin` | DateTimeField | `null=True`, `blank=True` |
| `estado` | CharField(20) | Opciones: `DRAFT`, `IN_PROGRESS`, `PAUSED`, `FINISHED`, `CANCELLED`; Por defecto: `DRAFT` |
| `observaciones` | TextField | `blank=True`, `default=''` |
| `prioridad` | CharField(10) | Opciones: `LOW`, `MEDIUM`, `HIGH`; Por defecto: `MEDIUM` |
| `usuario_responsable` | ForeignKey(User) | `on_delete=PROTECT`, `related_name='production_orders'` |
| `centro_trabajo` | ForeignKey(WorkCenter) | `on_delete=PROTECT`, `related_name='production_orders'` |
| `created_at` | DateTimeField | `auto_now_add` |
| `updated_at` | DateTimeField | `auto_now` |

### InventoryMovement

| Campo | Tipo | Restricciones |
|---|---|---|
| `id` | BigAutoField | Clave primaria |
| `producto` | ForeignKey(Product) | `on_delete=PROTECT`, `related_name='inventory_movements'` |
| `tipo_movimiento` | CharField(25) | Opciones: `INCOMING`, `OUTGOING`, `ADJUSTMENT`, `PRODUCTION_CONSUMPTION`, `PRODUCTION_INPUT` |
| `cantidad` | DecimalField(12, 2) | |
| `stock_anterior` | DecimalField(12, 2) | |
| `stock_nuevo` | DecimalField(12, 2) | |
| `motivo` | TextField | `blank=True`, `default=''` |
| `orden_produccion` | ForeignKey(ProductionOrder) | `on_delete=SET_NULL`, `null=True`, `blank=True`, `related_name='inventory_movements'` |
| `usuario` | ForeignKey(User) | `on_delete=PROTECT`, `related_name='inventory_movements'` |
| `fecha_movimiento` | DateTimeField | `auto_now_add` |
| `created_at` | DateTimeField | `auto_now_add` |
| `updated_at` | DateTimeField | `auto_now` |

## Reglas de negocio

### Validación de stock

Al iniciar una orden de producción (`POST /api/production-orders/{id}/start/`), el sistema valida que exista suficiente materia prima para TODOS los materiales requeridos en la BOM activa. Si algún material es insuficiente, la orden no puede iniciarse y el sistema devuelve una lista detallada de los materiales faltantes.

### Inventario automático al completar

Cuando una orden de producción se completa (`POST /api/production-orders/{id}/complete/`), el sistema automáticamente:
1. Genera movimientos `PRODUCTION_CONSUMPTION` por cada materia prima consumida (disminuye stock)
2. Genera un movimiento `PRODUCTION_INPUT` por el producto terminado (aumenta stock)
3. Actualiza las cantidades de stock correspondientes

### Exclusividad del centro de trabajo

Un centro de trabajo no puede tener más de una orden de producción en estado `IN_PROGRESS` al mismo tiempo. Intentar iniciar producción en un centro de trabajo ocupado devuelve un error 400.

### Soft delete (eliminación lógica)

Los productos utilizan `activo=False` para eliminación lógica en lugar de eliminación física. Esto evita la pérdida de datos en registros relacionados (BOMs, órdenes de producción, movimientos de inventario).

## Códigos de estado HTTP

| Código | Descripción | Cuándo ocurre |
|---|---|---|
| 200 | OK | GET, PUT, PATCH exitosos |
| 201 | Created | POST exitoso |
| 204 | No Content | DELETE exitoso |
| 400 | Bad Request | Error de validación, violación de regla de negocio |
| 401 | Unauthorized | Token JWT faltante o inválido |
| 403 | Forbidden | Autenticado pero sin permisos suficientes |
| 404 | Not Found | El recurso no existe |

## URL desplegada

La API se encuentra desplegada en:

**https://tanqueno-produccion.uaeftt-ute.site**

## Solución de problemas comunes

### "Couldn't import Django"

El entorno virtual no está activado o las dependencias no están instaladas:

```bash
source .venv/bin/activate
uv sync
```

### "Connection refused" en la base de datos

Asegúrate de que PostgreSQL esté ejecutándose:

```bash
sudo systemctl status postgresql
```

### "Role 'postgres' does not exist"

Crear el rol de PostgreSQL:

```bash
sudo -u postgres createuser --superuser postgres
```

### "Secret key is required"

Copia y configura el archivo `.env`:

```bash
cp .env.example .env
# Edita .env con tu SECRET_KEY
```

Genera una clave segura:

```bash
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Token inválido o expirado

Los tokens expiran después de 60 minutos. Usa el refresh token para obtener un nuevo access token:

```bash
curl -X POST https://tanqueno-produccion.uaeftt-ute.site/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "tu-refresh-token"}'
```

### Migraciones no aplicadas

```bash
uv run python manage.py migrate
```

### Puerto en uso

Usa un puerto diferente:

```bash
uv run python manage.py runserver 0.0.0.0:8080
```
