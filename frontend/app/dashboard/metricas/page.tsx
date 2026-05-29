"use client";

import { useState, useEffect, useCallback } from "react";
import { apiFetch } from "@/lib/api";

interface Cliente { id: string; name: string; instagram_username: string; }
interface MetricSummary {
  followers_count: number; reach_total: number; impressions_total: number;
  engagement_promedio: number; profile_views_total: number; website_clicks_total: number; dias: number;
}
interface MetricRow {
  id: string; date: string; followers_count: number; reach: number;
  impressions: number; engagement_rate: number; profile_views: number; website_clicks: number;
}

interface KPICardProps { label: string; value: string; sub?: string; icon: string; color: string; }
function KPICard({ label, value, sub, icon, color }: KPICardProps) {
  return (
    <div className={`rounded-xl bg-white p-5 shadow-sm border-l-4 ${color}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-500">{label}</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">{value}</p>
          {sub && <p className="mt-0.5 text-xs text-gray-400">{sub}</p>}
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
    </div>
  );
}

function formatNum(n: number) {
  if (n >= 1000000) return `${(n/1000000).toFixed(1)}M`;
  if (n >= 1000) return `${(n/1000).toFixed(1)}K`;
  return String(n);
}

export default function MetricasPage() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [clienteId, setClienteId] = useState("");
  const [days, setDays] = useState(7);
  const [summary, setSummary] = useState<MetricSummary | null>(null);
  const [historial, setHistorial] = useState<MetricRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [sincronizando, setSincronizando] = useState(false);

  useEffect(() => { apiFetch("/clients/").then(setClientes).catch(() => {}); }, []);

  const cargar = useCallback(async () => {
    if (!clienteId) { setSummary(null); setHistorial([]); return; }
    setLoading(true);
    try {
      const [sum, hist] = await Promise.all([
        apiFetch(`/metrics/summary?client_id=${clienteId}&days=${days}`),
        apiFetch(`/metrics/?client_id=${clienteId}`),
      ]);
      setSummary(sum);
      setHistorial(hist.slice(0, days));
    } catch { setSummary(null); }
    finally { setLoading(false); }
  }, [clienteId, days]);

  useEffect(() => { cargar(); }, [cargar]);

  async function handleSync() {
    if (!clienteId) return;
    setSincronizando(true);
    try {
      await apiFetch(`/metrics/sync?client_id=${clienteId}`, { method: "POST" });
      cargar();
    } catch (e: any) { alert(e.message); }
    finally { setSincronizando(false); }
  }

  const clienteActual = clientes.find((c) => c.id === clienteId);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Métricas</h1>
          {clienteActual && (
            <p className="mt-1 text-sm text-gray-500">@{clienteActual.instagram_username}</p>
          )}
        </div>
        <div className="flex gap-3">
          <select value={days} onChange={(e) => setDays(Number(e.target.value))}
            className="rounded-xl border border-gray-200 px-3 py-2 text-sm focus:border-brand focus:outline-none">
            <option value={7}>Últimos 7 días</option>
            <option value={14}>Últimos 14 días</option>
            <option value={30}>Últimos 30 días</option>
          </select>
          <select value={clienteId} onChange={(e) => setClienteId(e.target.value)}
            className="rounded-xl border border-gray-200 px-4 py-2 text-sm focus:border-brand focus:outline-none">
            <option value="">Selecciona un cliente</option>
            {clientes.map((c) => (
              <option key={c.id} value={c.id}>@{c.instagram_username}</option>
            ))}
          </select>
          {clienteId && (
            <button onClick={handleSync} disabled={sincronizando}
              className="rounded-xl border border-gray-200 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50">
              {sincronizando ? "Sincronizando..." : "↻ Sincronizar"}
            </button>
          )}
        </div>
      </div>

      {!clienteId ? (
        <div className="rounded-xl border-2 border-dashed border-gray-200 py-16 text-center">
          <p className="text-sm text-gray-500">Selecciona un cliente para ver sus métricas.</p>
        </div>
      ) : loading ? (
        <p className="text-sm text-gray-400">Cargando métricas...</p>
      ) : !summary || summary.dias === 0 ? (
        <div className="rounded-xl border-2 border-dashed border-gray-200 py-12 text-center">
          <p className="text-sm text-gray-500">No hay métricas para este cliente.</p>
          <button onClick={handleSync} disabled={sincronizando}
            className="mt-3 text-sm text-brand underline">
            Sincronizar desde Meta
          </button>
        </div>
      ) : (
        <>
          {/* KPI Cards */}
          <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
            <KPICard label="Seguidores" value={formatNum(summary.followers_count)}
              sub="actual" icon="👥" color="border-blue-400" />
            <KPICard label="Alcance" value={formatNum(summary.reach_total)}
              sub={`${days} días`} icon="📡" color="border-green-400" />
            <KPICard label="Impresiones" value={formatNum(summary.impressions_total)}
              sub={`${days} días`} icon="👁" color="border-purple-400" />
            <KPICard label="Engagement" value={`${summary.engagement_promedio}%`}
              sub="promedio" icon="❤️" color="border-red-400" />
            <KPICard label="Visitas perfil" value={formatNum(summary.profile_views_total)}
              sub={`${days} días`} icon="🔍" color="border-yellow-400" />
            <KPICard label="Clicks web" value={formatNum(summary.website_clicks_total)}
              sub={`${days} días`} icon="🔗" color="border-orange-400" />
          </div>

          {/* Tabla histórica */}
          {historial.length > 0 && (
            <div className="overflow-hidden rounded-xl bg-white shadow">
              <table className="w-full text-left text-sm">
                <thead className="bg-gray-50 text-xs font-medium uppercase tracking-wide text-gray-500">
                  <tr>
                    {["Fecha", "Seguidores", "Alcance", "Impresiones", "Engagement", "Perfil", "Web"].map((h) => (
                      <th key={h} className="px-4 py-3">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {historial.map((m) => (
                    <tr key={m.id} className="hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium text-gray-700">{m.date}</td>
                      <td className="px-4 py-2 text-gray-600">{formatNum(m.followers_count)}</td>
                      <td className="px-4 py-2 text-gray-600">{formatNum(m.reach)}</td>
                      <td className="px-4 py-2 text-gray-600">{formatNum(m.impressions)}</td>
                      <td className="px-4 py-2 text-gray-600">{m.engagement_rate}%</td>
                      <td className="px-4 py-2 text-gray-600">{formatNum(m.profile_views)}</td>
                      <td className="px-4 py-2 text-gray-600">{formatNum(m.website_clicks)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
