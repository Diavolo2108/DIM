import Image from "next/image";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <aside className="w-64 bg-black shadow-lg border-r-4 border-brand">
        <div className="p-4 border-b border-gray-800">
          <Image src="/logo.png" alt="Diavolo" width={200} height={60} className="w-full h-auto" priority />
          <p className="text-xs text-gray-400 mt-2 text-center">Social Manager</p>
        </div>
        <nav className="mt-4 space-y-1 px-4">
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
              className="block rounded-lg px-3 py-2 text-sm text-gray-300 hover:bg-gray-900 hover:text-brand transition-colors duration-200"
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
