'use client';
/**
 * app/dashboard/page.jsx
 * Dashboard principal — muestra documentos recientes,
 * estadísticas y acceso a todas las funciones.
 */
import { useState, useEffect, useCallback } from 'react';
import { useRouter }  from 'next/navigation';
import toast          from 'react-hot-toast';
import {
  FileText, Search, Bell, LogOut, Menu, X,
  Upload, ChevronRight, Clock, FileCheck,
  Users, BarChart2, Home, Settings, Folder,
  Download, Eye, MoreVertical, RefreshCw,
} from 'lucide-react';
import { docsService, authService } from '@/lib/api';
import { getUser, getToken, clearSession } from '@/lib/auth';
import styles from './dashboard.module.css';

// ── Skeleton loader ──────────────────────────────────────────
function Skeleton({ className }) {
  return <div className={`${styles.skeleton} ${className ?? ''}`} />;
}

// ── Tarjeta de estadística ───────────────────────────────────
function StatCard({ icon: Icon, label, value, color, loading }) {
  return (
    <div className={styles.statCard} style={{ '--accent': color }}>
      <div className={styles.statIcon}><Icon size={20} strokeWidth={1.5} /></div>
      <div className={styles.statBody}>
        <span className={styles.statLabel}>{label}</span>
        {loading
          ? <Skeleton className={styles.skeletonStat} />
          : <span className={styles.statValue}>{value}</span>
        }
      </div>
    </div>
  );
}

// ── Fila de documento ────────────────────────────────────────
function DocRow({ doc }) {
  const ext = doc.nombre?.split('.').pop()?.toUpperCase() ?? 'DOC';
  const badgeColor = {
    PDF: '#ef4444', DOCX: '#3b82f6', XLSX: '#10b981',
    PNG: '#8b5cf6', JPG: '#f59e0b',
  }[ext] ?? '#64748b';

  return (
    <div className={styles.docRow}>
      <div className={styles.docMain}>
        <span className={styles.docBadge} style={{ background: badgeColor }}>
          {ext}
        </span>
        <div className={styles.docInfo}>
          <span className={styles.docTitle}>{doc.titulo || doc.nombre}</span>
          <span className={styles.docMeta}>
            {doc.autor} · {formatDate(doc.fecha_subida)}
          </span>
        </div>
      </div>
      <div className={styles.docActions}>
        <button className={styles.iconBtn} title="Ver"><Eye size={15} /></button>
        <button className={styles.iconBtn} title="Descargar"><Download size={15} /></button>
        <button className={styles.iconBtn} title="Más"><MoreVertical size={15} /></button>
      </div>
    </div>
  );
}

// ── Utilidades ───────────────────────────────────────────────
function formatDate(iso) {
  if (!iso) return '—';
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit', month: 'short', year: 'numeric',
  }).format(new Date(iso));
}

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Inicio',       icon: Home    },
  { id: 'documents', label: 'Documentos',   icon: Folder  },
  { id: 'reports',   label: 'Reportes',     icon: BarChart2 },
  { id: 'users',     label: 'Usuarios',     icon: Users   },
  { id: 'settings',  label: 'Configuración',icon: Settings },
];

// ── Componente principal ─────────────────────────────────────
export default function DashboardPage() {
  const router = useRouter();
  const user   = getUser();

  const [docs,    setDocs]    = useState([]);
  const [stats,   setStats]   = useState(null);
  const [loading, setLoading] = useState(true);
  const [search,  setSearch]  = useState('');
  const [navOpen, setNavOpen] = useState(false);
  const [active,  setActive]  = useState('dashboard');

  // Carga documentos recientes desde ms_documentos (LUISA)
  const loadDocs = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await docsService.getAll({ limit: 8, order: 'desc' });
      // ms_documentos devuelve { documentos: [...], total: n }
      setDocs(data.documentos ?? data ?? []);
      setStats({
        total:    data.total     ?? (data.documentos ?? data).length,
        recientes: data.recientes ?? 0,
        usuarios: data.usuarios  ?? 0,
        pendientes: data.pendientes ?? 0,
      });
    } catch {
      // Si el ms aún no está listo mostramos datos de demostración
      setDocs(DEMO_DOCS);
      setStats(DEMO_STATS);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadDocs(); }, [loadDocs]);

  // Búsqueda con debounce
  useEffect(() => {
    if (!search.trim()) { loadDocs(); return; }
    const id = setTimeout(async () => {
      try {
        const { data } = await docsService.search(search);
        setDocs(data.documentos ?? data ?? []);
      } catch {
        setDocs(DEMO_DOCS.filter(d =>
          d.titulo.toLowerCase().includes(search.toLowerCase())
        ));
      }
    }, 400);
    return () => clearTimeout(id);
  }, [search, loadDocs]);

  const handleLogout = async () => {
    try { await authService.logout(getToken()); } catch { /* ignorar */ }
    clearSession();
    toast('Sesión cerrada.', { icon: '👋' });
    router.replace('/login');
  };

  const initials = user?.nombre
    ?.split(' ')
    .map(n => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase() ?? 'U';

  return (
    <div className={styles.layout}>
      {/* ── Sidebar ── */}
      <aside className={`${styles.sidebar} ${navOpen ? styles.sidebarOpen : ''}`}>
        <div className={styles.sidebarTop}>
          {/* Logo */}
          <div className={styles.sidebarLogo}>
            <div className={styles.logoMark}><FileText size={18} /></div>
            <span className={styles.logoText}>GestorDocs</span>
          </div>

          <button
            className={styles.closeNav}
            onClick={() => setNavOpen(false)}
            aria-label="Cerrar menú"
          >
            <X size={18} />
          </button>
        </div>

        <nav className={styles.nav} role="navigation" aria-label="Menú principal">
          {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={`${styles.navItem} ${active === id ? styles.navActive : ''}`}
              onClick={() => { setActive(id); setNavOpen(false); }}
            >
              <Icon size={18} strokeWidth={1.5} />
              <span>{label}</span>
              {active === id && <div className={styles.navIndicator} />}
            </button>
          ))}
        </nav>

        <div className={styles.sidebarFooter}>
          <div className={styles.userCard}>
            <div className={styles.avatar}>{initials}</div>
            <div className={styles.userInfo}>
              <span className={styles.userName}>{user?.nombre ?? 'Usuario'}</span>
              <span className={styles.userRole}>{user?.rol ?? 'sin rol'}</span>
            </div>
          </div>
          <button
            className={styles.logoutBtn}
            onClick={handleLogout}
            title="Cerrar sesión"
          >
            <LogOut size={16} />
          </button>
        </div>
      </aside>

      {/* Overlay móvil */}
      {navOpen && (
        <div
          className={styles.overlay}
          onClick={() => setNavOpen(false)}
          aria-hidden
        />
      )}

      {/* ── Main ── */}
      <main className={styles.main}>
        {/* Header */}
        <header className={styles.header}>
          <div className={styles.headerLeft}>
            <button
              className={styles.menuBtn}
              onClick={() => setNavOpen(true)}
              aria-label="Abrir menú"
            >
              <Menu size={20} />
            </button>
            <div className={styles.searchBox}>
              <Search size={16} className={styles.searchIcon} />
              <input
                type="search"
                placeholder="Buscar documentos…"
                className={styles.searchInput}
                value={search}
                onChange={e => setSearch(e.target.value)}
                aria-label="Buscar documentos"
              />
            </div>
          </div>

          <div className={styles.headerRight}>
            <button className={styles.headerBtn} aria-label="Notificaciones">
              <Bell size={18} />
              <span className={styles.notifDot} aria-hidden />
            </button>
            <div className={styles.headerAvatar}>{initials}</div>
          </div>
        </header>

        {/* Contenido */}
        <div className={styles.content}>
          {/* Bienvenida */}
          <div className={styles.welcome}>
            <div>
              <h1 className={styles.welcomeTitle}>
                Buenos días, {user?.nombre?.split(' ')[0] ?? 'bienvenido'} 👋
              </h1>
              <p className={styles.welcomeSub}>
                Aquí tienes el resumen de tus documentos de hoy.
              </p>
            </div>
            <button className={styles.uploadBtn}>
              <Upload size={16} />
              <span>Subir documento</span>
            </button>
          </div>

          {/* Stats */}
          <div className={styles.statsGrid}>
            <StatCard
              icon={FileText}
              label="Total documentos"
              value={stats?.total ?? '—'}
              color="var(--emerald-500)"
              loading={loading}
            />
            <StatCard
              icon={Clock}
              label="Subidos este mes"
              value={stats?.recientes ?? '—'}
              color="#3b82f6"
              loading={loading}
            />
            <StatCard
              icon={FileCheck}
              label="Pendientes de firma"
              value={stats?.pendientes ?? '—'}
              color="#f59e0b"
              loading={loading}
            />
            <StatCard
              icon={Users}
              label="Usuarios activos"
              value={stats?.usuarios ?? '—'}
              color="#8b5cf6"
              loading={loading}
            />
          </div>

          {/* Lista de documentos */}
          <div className={styles.section}>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>Documentos recientes</h2>
              <div className={styles.sectionActions}>
                <button
                  className={styles.refreshBtn}
                  onClick={loadDocs}
                  title="Actualizar"
                  disabled={loading}
                >
                  <RefreshCw size={14} className={loading ? styles.spin : ''} />
                </button>
                <button className={styles.viewAllBtn}>
                  Ver todos <ChevronRight size={14} />
                </button>
              </div>
            </div>

            <div className={styles.docList}>
              {loading
                ? Array.from({ length: 5 }).map((_, i) => (
                    <div key={i} className={styles.docRowSkeleton}>
                      <Skeleton className={styles.skeletonBadge} />
                      <div style={{ flex: 1, display:'flex', flexDirection:'column', gap:6 }}>
                        <Skeleton className={styles.skeletonTitle} />
                        <Skeleton className={styles.skeletonMeta} />
                      </div>
                    </div>
                  ))
                : docs.length === 0
                ? (
                    <div className={styles.emptyState}>
                      <FileText size={40} strokeWidth={1} />
                      <p>No se encontraron documentos.</p>
                    </div>
                  )
                : docs.map((doc, i) => <DocRow key={doc.id ?? i} doc={doc} />)
              }
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

// ── Datos demo (mientras ms_documentos no esté listo) ────────
const DEMO_DOCS = [
  { id:1, titulo:'Reglamento Académico 2024', nombre:'reglamento.pdf', autor:'Admin', fecha_subida:'2024-05-01' },
  { id:2, titulo:'Acta de Consejo — Marzo',   nombre:'acta_marzo.docx', autor:'Secretaría', fecha_subida:'2024-03-15' },
  { id:3, titulo:'Presupuesto Q1',            nombre:'presupuesto_q1.xlsx', autor:'Finanzas', fecha_subida:'2024-04-02' },
  { id:4, titulo:'Informe de Investigación',  nombre:'informe_inv.pdf', autor:'J. Pérez', fecha_subida:'2024-04-18' },
  { id:5, titulo:'Convocatoria Becas 2024',   nombre:'becas_convocatoria.pdf', autor:'Bienestar', fecha_subida:'2024-04-25' },
];
const DEMO_STATS = { total: 128, recientes: 14, pendientes: 3, usuarios: 24 };
