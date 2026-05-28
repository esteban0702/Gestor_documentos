import './globals.css';
import { Toaster } from 'react-hot-toast';

export const metadata = {
  title: 'GestorDocs UNAL',
  description: 'Sistema de gestión documental universitario',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              fontFamily: 'var(--font-body)',
              fontSize: '14px',
              borderRadius: 'var(--radius-md)',
              background: '#1e293b',
              color: '#f8fafc',
              boxShadow: 'var(--shadow-lg)',
            },
            success: { iconTheme: { primary: '#10b981', secondary: '#f8fafc' } },
            error:   { iconTheme: { primary: '#ef4444', secondary: '#f8fafc' } },
          }}
        />
      </body>
    </html>
  );
}
