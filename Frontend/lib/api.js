/**
 * lib/api.js
 * Cliente HTTP centralizado para todos los microservicios.
 * Cada sección se conecta al ms correspondiente.
 *
 * Cuando un compañero levante su servicio, solo cambias
 * la URL en .env — el código no cambia.
 */
import axios from 'axios';
import Cookies from 'js-cookie';

// ── Instancias por microservicio ─────────────────────────────
const authApi = axios.create({
  baseURL: process.env.NEXT_PUBLIC_AUTH_API_URL || 'http://localhost:8001',
  timeout: 10_000,
  headers: { 'Content-Type': 'application/json' },
});

const docsApi = axios.create({
  baseURL: process.env.NEXT_PUBLIC_DOCS_API_URL || 'http://localhost:8002',
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
});

const utilsApi = axios.create({
  baseURL: process.env.NEXT_PUBLIC_UTILS_API_URL || 'http://localhost:8003',
  timeout: 30_000, // extracción puede tardar más
});

// ── Interceptor: agrega el token en cada request ─────────────
[docsApi, utilsApi].forEach((instance) => {
  instance.interceptors.request.use((config) => {
    const token = Cookies.get('auth_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  });
});

// ── Interceptor: maneja 401 globalmente ──────────────────────
[authApi, docsApi, utilsApi].forEach((instance) => {
  instance.interceptors.response.use(
    (res) => res,
    (error) => {
      if (error.response?.status === 401) {
        Cookies.remove('auth_token');
        Cookies.remove('user_data');
        // Redirige al login si el token expiró
        if (typeof window !== 'undefined') {
          window.location.href = '/login?expired=true';
        }
      }
      return Promise.reject(error);
    }
  );
});

// ── Servicios de Autenticación (ms_autenticacion — JOHN) ─────
export const authService = {
  /**
   * Login con usuario y contraseña.
   * Espera: { usuario, password }
   * Retorna: { token, usuario: { id, nombre, rol } }
   */
  login: (credentials) => authApi.post('/auth/login', credentials),

  /**
   * Valida si el token actual sigue activo.
   * ms_autenticacion debe tener este endpoint.
   */
  validateToken: (token) =>
    authApi.get('/auth/validate', {
      headers: { Authorization: `Bearer ${token}` },
    }),

  /** Cierra sesión en el servidor (invalida el token) */
  logout: (token) =>
    authApi.post('/auth/logout', {}, {
      headers: { Authorization: `Bearer ${token}` },
    }),

  // ── Gestión de usuarios (solo admin) ──
  getUsers:       ()       => authApi.get('/usuarios'),
  createUser:     (data)   => authApi.post('/usuarios', data),
  updateUser:     (id, data) => authApi.put(`/usuarios/${id}`, data),
  deactivateUser: (id)     => authApi.patch(`/usuarios/${id}/inactivar`),
};

// ── Servicios de Documentos (ms_documentos — LUISA) ──────────
export const docsService = {
  /** Lista documentos con filtros opcionales */
  getAll: (params) => docsApi.get('/documentos', { params }),

  /** Obtiene un documento por ID */
  getById: (id) => docsApi.get(`/documentos/${id}`),

  /**
   * Sube un documento. Usa FormData porque incluye el archivo.
   * ms_documentos llama a ms_utils para extraer el texto.
   */
  upload: (formData) =>
    docsApi.post('/documentos', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  /** Actualiza metadata de un documento */
  update: (id, data) => docsApi.put(`/documentos/${id}`, data),

  /** Elimina un documento */
  delete: (id) => docsApi.delete(`/documentos/${id}`),

  /** Busca en el contenido de los documentos */
  search: (query) => docsApi.get('/documentos/buscar', { params: { q: query } }),
};

// ── Servicios utilitarios (ms_utils — ALEXIS) ────────────────
export const utilsService = {
  /** Extrae texto de un PDF */
  extractPdfText: (formData) => utilsApi.post('/utils/extract/pdf', formData),

  /** Extrae texto de una imagen */
  extractImageText: (formData) => utilsApi.post('/utils/extract/image', formData),
};

export { authApi, docsApi, utilsApi };
