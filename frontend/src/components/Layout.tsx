import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { Activity, Bug, ClipboardList, Database, FileInput, Gauge, KeyRound, LogOut, Server, Settings } from "lucide-react";
import { DEMO_MODE, clearToken } from "../api/client";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: Gauge },
  { to: "/assets", label: "Assets", icon: Server },
  { to: "/vulnerabilities", label: "Vulnerabilities", icon: Activity },
  { to: "/cves", label: "CVEs", icon: Bug },
  { to: "/remediation", label: "Remediation", icon: ClipboardList },
  { to: "/imports", label: "Imports", icon: FileInput },
  { to: "/settings", label: "Settings", icon: Settings }
];

export function Layout() {
  const navigate = useNavigate();

  function logout() {
    clearToken();
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-bg text-ink">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-surface lg:block">
        <div className="flex h-16 items-center gap-3 border-b border-line px-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-panel text-signal">
            <Database size={18} />
          </div>
          <div>
            <div className="text-sm font-semibold uppercase tracking-wide text-white">VulnScope</div>
            <div className="text-xs text-slate-400">Exposure management</div>
          </div>
        </div>
        <nav className="space-y-1 p-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium ${isActive ? "bg-panel text-white" : "text-slate-300 hover:bg-panel/70 hover:text-white"}`
                }
              >
                <Icon size={17} />
                {item.label}
              </NavLink>
            );
          })}
        </nav>
      </aside>
      <main className="lg:pl-64">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-line bg-surface px-4 lg:px-8">
          <div>
            <div className="text-sm font-semibold text-white">VulnScope</div>
            <div className="text-xs text-slate-400">Defensive exposure management</div>
          </div>
          <div className="flex items-center gap-2">
            {DEMO_MODE && <span className="rounded-md border border-signal/40 bg-panel px-2 py-1 text-xs font-semibold text-signal">Demo Mode</span>}
            {!DEMO_MODE && (
              <button onClick={logout} className="focus-ring inline-flex items-center gap-2 rounded-md border border-line bg-panel px-3 py-2 text-sm text-slate-200 hover:border-signal hover:text-white">
                <LogOut size={16} />
                Sign out
              </button>
            )}
          </div>
        </header>
        <div className="mx-auto max-w-7xl px-4 py-6 lg:px-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export function PageHeader({ title, actions }: { title: string; actions?: React.ReactNode }) {
  return (
    <div className="mb-5 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
      <h1 className="text-2xl font-semibold text-white">{title}</h1>
      {actions}
    </div>
  );
}

export function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <section className={`rounded-md border border-line bg-surface p-4 ${className}`}>{children}</section>;
}
// Project version: VulnScope V1.5








