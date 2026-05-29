"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

interface Campana {
  id: string;
  name: string;
  objetivo: string;
  status: string;
  frecuencia: string | null;
  created_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  PLANIFICACION: "bg-blue-100 text-blue-800",
  ACTIVA: "bg-green-100 text-green-800",
  COMPLETADA: "bg-gray-100 text-gray-700",
  CANCELADA: "bg-red-100 text-red-800",
};

export default function CampanasPage() {
  const router = useRouter();
  const [campanas, setCampanas] = useState<Campana[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch("/campaigns/")
      .then(setCampanas)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campañas</h1>
          <p className="mt-1 text-sm text-gray-500">{campanas.length} campañas registradas</p>
        </div>
        <button
          onClick={() => router.push("/dashboard/campanas/nueva")}
          className="rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark"
        >
          + Nueva campaña
        </button>
      </div>

      {loading ? (
        <p className="text-sm text-gray-400">Cargando...</p>
      ) : campanas.length === 0 ? (
        <div className="rounded-xl border-2 border-dashed border-gray-200 py-16 text-center">
          <p className="text-sm text-gray-500">No hay campañas aún.</p>
          <button
            onClick={() => router.push("/dashboard/campanas/nueva")}
            className="mt-3 text-sm text-brand underline"
          >
            Planificar primera campaña con IA
          </button>
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl bg-white shadow">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 text-xs font-medium uppercase tracking-wide text-gray-500">
              <tr>
                <th className="px-6 py-3">Campaña</th>
                <th className="px-6 py-3">Objetivo</th>
                <th className="px-6 py-3">Frecuencia</th>
                <th className="px-6 py-3">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {campanas.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900">{c.name}</td>
                  <td className="max-w-xs truncate px-6 py-4 text-gray-500">{c.objetivo}</td>
                  <td className="px-6 py-4 text-gray-500">{c.frecuencia ?? "—"}</td>
                  <td className="px-6 py-4">
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLORS[c.status] ?? "bg-gray-100 text-gray-700"}`}>
                      {c.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
