/**
 * lib/auth.js
 * Utilidades de sesión del lado del cliente.
 * Guarda/lee el token y datos del usuario en cookies
 * (más seguras que localStorage para auth).
 */
import Cookies from 'js-cookie';

const TOKEN_KEY    = 'auth_token';
const USER_KEY     = 'user_data';
const SESSION_MINS = Number(process.env.NEXT_PUBLIC_SESSION_TIMEOUT) || 15;

/** Guarda token + datos del usuario tras login exitoso */
export function saveSession(token, userData) {
  const expires = new Date(Date.now() + SESSION_MINS * 60 * 1000);
  // secure:true en producción (HTTPS), sameSite evita CSRF
  Cookies.set(TOKEN_KEY, token, {
    expires,
    sameSite: 'Strict',
    secure: process.env.NODE_ENV === 'production',
  });
  Cookies.set(USER_KEY, JSON.stringify(userData), {
    expires,
    sameSite: 'Strict',
    secure: process.env.NODE_ENV === 'production',
  });
}

/** Lee el token almacenado */
export function getToken() {
  return Cookies.get(TOKEN_KEY) || null;
}

/** Lee los datos del usuario (objeto parseado) */
export function getUser() {
  const raw = Cookies.get(USER_KEY);
  try { return raw ? JSON.parse(raw) : null; }
  catch { return null; }
}

/** Comprueba si hay sesión activa */
export function isAuthenticated() {
  return Boolean(getToken());
}

/** Elimina la sesión local */
export function clearSession() {
  Cookies.remove(TOKEN_KEY);
  Cookies.remove(USER_KEY);
}

/** Roles disponibles en el sistema */
export const ROLES = {
  ADMIN:    'admin',
  DOCENTE:  'docente',
  ESTUDIANTE: 'estudiante',
};

/** Comprueba si el usuario tiene un rol específico */
export function hasRole(role) {
  return getUser()?.rol === role;
}
