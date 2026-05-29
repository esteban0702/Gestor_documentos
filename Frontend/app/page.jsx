import { redirect } from 'next/navigation';

// La raíz redirige al login. Si hay token válido,
// el middleware lo manda directamente al dashboard.
export default function RootPage() {
  redirect('/login');
}
