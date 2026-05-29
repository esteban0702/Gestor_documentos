#  ms_autenticacion — GestorDocs

Microservicio de autenticación JWT para el sistema GestorDocs.  
**Responsable:** Jhon Montes | **Puerto:** `8001`

---

## Arquitectura MVC

```
auth_service/
├── app/
│   ├── models/
│   │   └── user.py              ← Model: tabla usuarios en BD
│   ├── views/
│   │   └── schemas.py           ← View: esquemas JSON entrada/salida
│   ├── controllers/
│   │   └── auth_controller.py   ← Controller: endpoints de la API
│   └── services/
│       └── security.py          ← Service: JWT y hashing de contraseñas
├── database.py                  ← Conexión a PostgreSQL (Supabase)
├── main.py                      ← Punto de entrada
├── requirements.txt
└── .env                         ← Variables de entorno (no subir a Git)
```

---

## Requisitos

| Herramienta | Versión |
|---|---|
| Python | 3.10+ |
| pip | cualquiera |

---

## Instalación paso a paso

### 1. Crear y activar entorno virtual

```powershell
# Crear
python -m venv venv

# Activar en Windows PowerShell
.\venv\Scripts\Activate.ps1

# Activar en Windows CMD
venv\Scripts\activate.bat

# Activar en Mac/Linux
source venv/bin/activate
```

> Debes ver `(venv)` al inicio de la línea antes de continuar.

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=postgresql://usuario:password@host:5432/postgres?sslmode=require
SECRET_KEY=genera_con_python_-c_"import secrets;print(secrets.token_hex(32))"
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> Para generar una SECRET_KEY segura:
> ```powershell
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 4. Correr el microservicio

```powershell
uvicorn main:app --reload --port 8001
```

Swagger disponible en: **http://localhost:8001/docs**  
Health check en: **http://localhost:8001/**

---

## 🔌 Endpoints — Contrato para el frontend (Raúl)

### POST `/auth/login`
Inicia sesión y retorna el JWT.

**Request:**
```json
{
  "usuario": "Jhon",
  "password": "asd123"
}
```

**Response 200:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "usuario": {
    "id": "128bec1c-9f55-46e3-85a8-cc62306a56ce",
    "nombre": "Jhon Montes",
    "rol": "admin"
  }
}
```

**Response 401:** Usuario o contraseña incorrectos  
**Response 403:** Usuario inactivo

---

### POST `/auth/register`
Crea un nuevo usuario.

**Request:**
```json
{
  "usuario": "jperez",
  "nombre": "Juan Pérez",
  "contrasena": "asd123",
  "perfil": "admin"
}
```

**Response 201:** Datos del usuario creado  
**Response 400:** El usuario ya está registrado

---

### GET `/auth/validate`
Verifica si el token sigue activo. Requiere JWT en el header.

**Header:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "valid": true,
  "usuario": {
    "id": "128bec1c-...",
    "nombre": "Jhon Montes",
    "rol": "admin"
  }
}
```

**Response 401:** Token inválido o expirado

---

### POST `/auth/logout`
Cierra la sesión. Requiere JWT.

**Response 200:**
```json
{
  "message": "Sesión cerrada para Jhon."
}
```

---

### GET `/auth/usuarios`
Lista todos los usuarios. Solo para perfil `admin`.

**Header:** `Authorization: Bearer <token>`

---

### PATCH `/auth/usuarios/{usuario}/inactivar`
Inactiva un usuario. Solo para perfil `admin`.

---

### GET `/health/db`
Verifica que la conexión a la base de datos esté activa.

**Response:**
```json
{
  "database": "conectada "
}
```

---

## 🔐 Cómo usar el JWT en Swagger

1. Llama a `POST /auth/login` y copia el valor del campo `token`
2. Haz clic en el botón **Authorize ** (arriba a la derecha)
3. Pega el token y haz clic en **Authorize**
4. Ahora puedes probar cualquier ruta protegida

---

## 🌐 CORS configurado para

```
http://localhost:3000   ← Frontend de Esteban (Next.js)
```

---

## Problemas comunes

| Error | Causa | Solución |
|---|---|---|
| `Host desconocido` | DNS bloqueado o `.env` incorrecto | Verificar URL en `.env`, cambiar DNS a 8.8.8.8 |
| `UnknownHashError` | bcrypt incompatible | `pip install bcrypt==4.0.1` |
| `(venv)` no aparece | Entorno no activado | Ejecutar `.\venv\Scripts\Activate.ps1` primero |
| `403 Forbidden` | Campo `estado` en BD con mayúscula | Ya corregido con `.lower()` en el controller |
| `401 Unauthorized` | Token no enviado o expirado | Usar el botón Authorize en Swagger |

