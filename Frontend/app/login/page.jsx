'use client';
import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import toast from 'react-hot-toast';
import { Eye, EyeOff, FileText, Lock, User, AlertCircle, FlaskConical } from 'lucide-react';
import { authService } from '@/lib/api';
import { saveSession, isAuthenticated } from '@/lib/auth';
import styles from './login.module.css';

// ── Usuarios demo (mientras los microservicios no estén listos) ──
const DEMO_USERS = [
  { usuario: 'admin',    password: 'admin123',   nombre: 'Admin Sistema',   rol: 'admin'      },
  { usuario: 'docente',  password: 'docente123', nombre: 'Juan Pérez',      rol: 'docente'    },
  { usuario: 'estudiante', password: 'est123',   nombre: 'Laura Gómez',     rol: 'estudiante' },
];

export default function LoginPage() {
  const router       = useRouter();
  const searchParams = useSearchParams();

  const [form, setForm]       = useState({ usuario: '', password: '' });
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');
  const [showDemo, setShowDemo] = useState(false);

  useEffect(() => {
    if (isAuthenticated()) router.replace('/dashboard');
  }, [router]);

  useEffect(() => {
    if (searchParams.get('expired') === 'true') {
      toast.error('Tu sesión expiró. Inicia sesión de nuevo.');
    }
  }, [searchParams]);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    if (error) setError('');
  };

  // ── Login real contra ms_autenticacion ──
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.usuario.trim() || !form.password) {
      setError('Completa usuario y contraseña.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const { data } = await authService.login(form);
      saveSession(data.token, data.usuario);
      toast.success(`¡Bienvenido, ${data.usuario.nombre}!`);
      router.replace(searchParams.get('redirect') || '/dashboard');
    } catch (err) {
      // Si el microservicio no está disponible, ofrece modo demo
      if (!err.response) {
        setError('No hay conexión con el servidor.');
        setShowDemo(true);
        return;
      }
      const msg =
        err.response?.status === 401 ? 'Usuario o contraseña incorrectos.' :
        err.response?.status === 403 ? 'Tu cuenta está inactiva.' :
        'Error del servidor. Intenta más tarde.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  // ── Login demo (sin microservicio) ──
  const loginDemo = (demoUser) => {
    const fakeToken = 'demo_token_' + Date.now();
    saveSession(fakeToken, { id: 0, nombre: demoUser.nombre, rol: demoUser.rol });
    toast.success(`Modo demo — bienvenido, ${demoUser.nombre}!`);
    router.replace('/dashboard');
  };

  // Autocompletar campos con credenciales demo
  const fillDemo = (demoUser) => {
    setForm({ usuario: demoUser.usuario, password: demoUser.password });
    setError('');
  };

  return (
    <div className={styles.page}>
      {/* Panel izquierdo */}
      <div className={styles.branding}>
        <div className={styles.brandingInner}>
          <div className={styles.logo}><FileText size={32} strokeWidth={1.5} /></div>
          <h1 className={styles.brandTitle}>GestorDocs</h1>
          <p className={styles.brandSub}>Sistema de gestión documental universitario</p>
          <div className={styles.featureList}>
            {[
              { icon: '🔒', text: 'Acceso seguro con tokens JWT' },
              { icon: '📄', text: 'Almacenamiento centralizado de documentos' },
              { icon: '🔍', text: 'Búsqueda inteligente en el contenido' },
              { icon: '⚡', text: 'Extracción automática de texto PDF' },
            ].map((f) => (
              <div key={f.text} className={styles.featureItem}>
                <span className={styles.featureIcon}>{f.icon}</span>
                <span>{f.text}</span>
              </div>
            ))}
          </div>
        </div>
        <div className={styles.geo1} /><div className={styles.geo2} /><div className={styles.geo3} />
      </div>

      {/* Panel derecho */}
      <div className={styles.formPanel}>
        <div className={styles.formCard}>
          <div className={styles.mobileLogo}>
            <FileText size={22} strokeWidth={1.5} /><span>GestorDocs</span>
          </div>

          <div className={styles.formHeader}>
            <h2 className={styles.formTitle}>Iniciar sesión</h2>
            <p className={styles.formSubtitle}>Ingresa tus credenciales institucionales</p>
          </div>

          <form onSubmit={handleSubmit} noValidate className={styles.form}>
            {error && (
              <div className={styles.errorBanner} role="alert">
                <AlertCircle size={16} /><span>{error}</span>
              </div>
            )}

            <div className={styles.field}>
              <label htmlFor="usuario" className={styles.label}>Usuario</label>
              <div className={styles.inputWrapper}>
                <User size={16} className={styles.inputIcon} />
                <input id="usuario" name="usuario" type="text" autoComplete="username"
                  placeholder="ej. jperez" value={form.usuario}
                  onChange={handleChange} className={styles.input} disabled={loading} />
              </div>
            </div>

            <div className={styles.field}>
              <div className={styles.labelRow}>
                <label htmlFor="password" className={styles.label}>Contraseña</label>
              </div>
              <div className={styles.inputWrapper}>
                <Lock size={16} className={styles.inputIcon} />
                <input id="password" name="password" type={showPwd ? 'text' : 'password'}
                  autoComplete="current-password" placeholder="••••••••"
                  value={form.password} onChange={handleChange}
                  className={`${styles.input} ${styles.inputPwd}`} disabled={loading} />
                <button type="button" onClick={() => setShowPwd(v => !v)}
                  className={styles.eyeBtn} aria-label={showPwd ? 'Ocultar' : 'Mostrar'}>
                  {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button type="submit" className={styles.submitBtn} disabled={loading}>
              {loading ? <span className={styles.spinner} /> : 'Ingresar'}
            </button>
          </form>

          {/* ── Sección modo demo ── */}
          <div className={styles.demoSection}>
            <button
              className={styles.demoToggle}
              onClick={() => setShowDemo(v => !v)}
              type="button"
            >
              <FlaskConical size={14} />
              <span>Modo demo — microservicios no disponibles</span>
              <span className={styles.demoChevron}>{showDemo ? '▲' : '▼'}</span>
            </button>

            {showDemo && (
              <div className={styles.demoBox}>
                <p className={styles.demoHint}>
                  Selecciona un usuario para ingresar sin microservicio:
                </p>
                {DEMO_USERS.map((u) => (
                  <div key={u.usuario} className={styles.demoRow}>
                    <div className={styles.demoInfo}>
                      <span className={styles.demoName}>{u.nombre}</span>
                      <span className={styles.demoRole}>{u.rol}</span>
                    </div>
                    <div className={styles.demoBtns}>
                      <button
                        className={styles.fillBtn}
                        onClick={() => fillDemo(u)}
                        title="Autocompletar campos"
                      >
                        Rellenar
                      </button>
                      <button
                        className={styles.enterBtn}
                        onClick={() => loginDemo(u)}
                      >
                        Entrar →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
