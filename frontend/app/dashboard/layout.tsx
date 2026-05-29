// Sprint 1-3: se agrega verificacion de sesion y sidebar de navegacion
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-gray-100">
      <aside className="w-64 bg-white shadow-sm">
        <div className="p-6">
          <h2 className="text-lg font-bold text-gray-900">Diavolo</h2>
          <p className="text-xs text-gray-400">Instagram Manager</p>
        </div>
        <nav className="mt-2 space-y-1 px-4">
          {[
            { href: "/dashboard/clientes", label: "Clientes" },
            { href: "/dashboard/campanas", label: "Campañas" },
            { href: "/dashboard/contenido", label: "Contenido" },
            { href: "/dashboard/calendario", label: "Calendario" },
            { href: "/dashboard/inbox", label: "Inbox" },
            { href: "/dashboard/metricas", label: "Métricas" },
            { href: "/dashboard/configuracion", label: "Configuración" },
          ].map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="block rounded-lg px-3 py-2 text-sm text-gray-700 hover:bg-gray-100"
            >
              {item.label}
            </a>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
