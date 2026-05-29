# 📚 GestorDocs — Frontend (RAUL)

Guía completa paso a paso para instalar, configurar y correr el frontend.

---

## 🗂 Arquitectura del sistema

```
┌─────────────────┐     ┌───────────────────┐     ┌──────────────────┐
│  FRONTEND       │────▶│ ms_autenticacion   │     │ ms_documentos    │
│  Next.js (RAUL) │     │ Python (JOHN)      │     │ Python (LUISA)   │
│  :3000          │────▶│ :8001              │────▶│ :8002            │
└─────────────────┘     └───────────────────┘     └──────────────────┘
                                                          │
                         ┌───────────────────┐     ┌─────▼────────────┐
                         │ ms_utils (ALEXIS) │     │ Base de datos     │
                         │ Python  :8003     │     │ PostgreSQL (ELKIN)│
                         └───────────────────┘     └──────────────────┘
```

---

## ✅ Pre-requisitos

Instala esto antes de continuar:

| Herramienta | Versión mínima | Descarga |
|---|---|---|
| Node.js | 18.17+ | https://nodejs.org |
| npm | 9+ (viene con Node) | — |
| Git | cualquiera | https://git-scm.com |

Verifica la instalación:
```bash
node -v   # debe mostrar v18.x.x o superior
npm -v    # debe mostrar 9.x.x o superior
```

---

## 🚀 Instalación paso a paso

### 1. Copiar los archivos del proyecto

Copia la carpeta `gestor-docs` a donde quieras trabajar. Por ejemplo:
```bash
# Mueve la carpeta a tu escritorio o a donde prefieras
cd ~/Desktop
# Ya tienes la carpeta gestor-docs aquí
cd gestor-docs
```

### 2. Instalar dependencias

```bash
npm install
```

Esto descarga automáticamente:
- `next` — framework React con SSR
- `axios` — cliente HTTP para conectar los microservicios
- `js-cookie` — manejo seguro de tokens en el navegador
- `react-hot-toast` — notificaciones bonitas
- `lucide-react` — íconos

### 3. Configurar variables de entorno

```bash
# Copia el archivo de ejemplo
cp .env.example .env.local
```

Abre `.env.local` y ajusta las URLs según donde corran los microservicios:
```env
# URL del microservicio de John (autenticación)
NEXT_PUBLIC_AUTH_API_URL=http://localhost:8001

# URL del microservicio de Luisa (documentos)
NEXT_PUBLIC_DOCS_API_URL=http://localhost:8002

# URL del microservicio de Alexis (utilidades)
NEXT_PUBLIC_UTILS_API_URL=http://localhost:8003
```

> **Nota**: mientras los compañeros no tengan su microservicio listo, el
> dashboard muestra datos de demostración automáticamente. El login
> mostrará error de conexión (esperado).

### 4. Correr en desarrollo

```bash
npm run dev
```

Abre el navegador en: **http://localhost:3000**

Serás redirigido automáticamente a `/login`.

---

## 📁 Estructura del proyecto

```
gestor-docs/
│
├── app/                          ← Páginas (Next.js App Router)
│   ├── globals.css               ← Estilos globales y tokens de diseño
│   ├── layout.jsx                ← Layout raíz (fuentes, toasts)
│   ├── page.jsx                  ← Redirige a /login
│   ├── login/
│   │   ├── page.jsx              ← Página de login ✅
│   │   └── login.module.css      ← Estilos del login
│   └── dashboard/
│       ├── page.jsx              ← Dashboard principal ✅
│       └── dashboard.module.css  ← Estilos del dashboard
│
├── lib/
│   ├── api.js     ← Cliente HTTP — conexión a todos los microservicios
│   └── auth.js    ← Manejo de sesión y cookies
│
├── middleware.js  ← Protección de rutas (sin token → login)
│
├── .env.example   ← Plantilla de variables de entorno
├── .env.local     ← Tu configuración local (NO subir a Git)
├── next.config.mjs
└── package.json
```

---

## 🔌 Cómo conectar cada microservicio

### ms_autenticacion (JOHN — :8001)

El login llama a este endpoint:
```
POST http://localhost:8001/auth/login
Body: { "usuario": "jperez", "password": "mi_clave" }
```

**Respuesta esperada (lo que debe devolver John):**
```json
{
  "token": "eyJhbGc...",
  "usuario": {
    "id": 1,
    "nombre": "Juan Pérez",
    "rol": "docente"
  }
}
```

Otros endpoints que se usan:
```
GET  /auth/validate        ← valida si el token sigue activo
POST /auth/logout          ← invalida el token en servidor
GET  /usuarios             ← lista usuarios (admin)
POST /usuarios             ← crea usuario
PUT  /usuarios/:id         ← edita usuario
PATCH /usuarios/:id/inactivar ← inactiva usuario
```

### ms_documentos (LUISA — :8002)

El dashboard llama a:
```
GET http://localhost:8002/documentos?limit=8&order=desc
```

**Respuesta esperada:**
```json
{
  "documentos": [
    {
      "id": 1,
      "titulo": "Reglamento 2024",
      "nombre": "reglamento.pdf",
      "autor": "Admin",
      "fecha_subida": "2024-05-01T10:00:00Z",
      "tipo_documento": "PDF",
      "contenido": "...(texto extraído)..."
    }
  ],
  "total": 128,
  "recientes": 14,
  "pendientes": 3,
  "usuarios": 24
}
```

### ms_utils (ALEXIS — :8003)

Se llama indirectamente desde ms_documentos. El frontend puede usarlo para:
```
POST /utils/extract/pdf     ← sube un PDF, devuelve texto
POST /utils/extract/image   ← sube una imagen, devuelve texto
```

---

## 🔐 Seguridad implementada

| Medida | Descripción |
|---|---|
| **JWT en cookies** | Token guardado en cookie `HttpOnly`-compatible con `SameSite: Strict` |
| **Middleware de rutas** | Next.js middleware bloquea rutas protegidas si no hay token |
| **Interceptor 401** | Si el token expira, redirige al login automáticamente |
| **Timeout de sesión** | Configurable en `.env.local` (por defecto 15 min) |
| **HTTPS en producción** | `secure: true` en cookies cuando `NODE_ENV=production` |
| **Sin localStorage** | Nunca se usa localStorage para datos de auth |

---

## 🏗 Comandos útiles

```bash
npm run dev      # Desarrollo con hot-reload en :3000
npm run build    # Compilar para producción
npm run start    # Correr el build de producción
npm run lint     # Verificar errores de código
```

---

## 🌐 CORS — Importante para los compañeros

Los microservicios en Python deben permitir peticiones desde el frontend.
Cada compañero debe agregar en su microservicio FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🚢 Despliegue (cuando estén listos)

```bash
# 1. Construir para producción
npm run build

# 2. Iniciar servidor de producción
npm run start   # corre en :3000

# O con PM2 para que quede siempre activo:
npm install -g pm2
pm2 start "npm run start" --name gestor-frontend
pm2 save
```

---

## 🐛 Problemas comunes

| Error | Causa | Solución |
|---|---|---|
| "No se pudo conectar al servidor" | ms_autenticacion no está corriendo | Levanta el microservicio de John primero |
| El dashboard muestra datos demo | ms_documentos no responde | Es normal. Datos reales aparecen cuando Luisa levante su servicio |
| Error de CORS | Microservicio sin CORS configurado | Agregar middleware CORS (ver sección arriba) |
| Cookie no se guarda | HTTP en producción | Usar HTTPS o cambiar `secure: false` en `lib/auth.js` |

---

Hecho con ❤️ — RAUL (Frontend)
