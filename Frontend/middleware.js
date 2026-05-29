/**
 * middleware.js
 * Protege rutas. Se ejecuta en el edge de Next.js
 * antes de que la página se renderice.
 *
 * - Si no hay token → redirige a /login
 * - Si hay token y va a /login → redirige a /dashboard
 */
import { NextResponse } from 'next/server';

const PUBLIC_ROUTES  = ['/login'];
const PROTECTED_PATH = '/dashboard';

export function middleware(request) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get('auth_token')?.value;

  const isPublic    = PUBLIC_ROUTES.some((r) => pathname.startsWith(r));
  const isProtected = pathname.startsWith(PROTECTED_PATH);

  // Ruta protegida sin token → login
  if (isProtected && !token) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Ya autenticado intenta ir al login → dashboard
  if (isPublic && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
