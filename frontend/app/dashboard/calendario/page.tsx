"use client";

import { useState, useEffect, useCallback } from "react";
import { apiFetch } from "@/lib/api";
import { CalendarGrid } from "@/components/calendar/CalendarGrid";
import { PostEditModal } from "@/components/calendar/PostEditModal";
import { CalendarPost } from "@/components/calendar/types";

interface Cliente { id: string; name: string; instagram_username: string; }

const MESES = [
  "Enero","Febrero","Marzo","Abril","Mayo","Junio",
  "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre",
];

function toMonthParam(year: number, month: number) {
  return `${year}-${String(month + 1).padStart(2, "0")}`;
}

export default function CalendarioPage() {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth()); // 0-indexed
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [clienteId, setClienteId] = useState("");
  const [posts, setPosts] = useState<CalendarPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [editandoPost, setEditandoPost] = useState<CalendarPost | null>(null);

  useEffect(() => { apiFetch("/clients/").then(setClientes).catch(() => {}); }, []);

  const cargarPosts = useCallback(async () => {
    if (!clienteId) { setPosts([]); return; }
    setLoading(true);
    try {
      const data = await apiFetch(`/posts/?client_id=${clienteId}&month=${toMonthParam(year, month)}`);
      setPosts(data);
    } catch { setPosts([]); }
    finally { setLoading(false); }
  }, [clienteId, year, month]);

  useEffect(() => { cargarPosts(); }, [cargarPosts]);

  function navMes(delta: number) {
    let m = month + delta;
    let y = year;
    if (m < 0) { m = 11; y--; }
    if (m > 11) { m = 0; y++; }
    setMonth(m);
    setYear(y);
  }

  function handlePostUpdated(updated: CalendarPost) {
    setPosts((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
  }

  const statusSummary = {
    programado: posts.filter((p) => p.status === "PROGRAMADO").length,
    publicado: posts.filter((p) => p.status === "PUBLICADO").length,
    fallido: posts.filter((p) => p.status === "FALLIDO").length,
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Calendario</h1>
          {posts.length > 0 && (
            <div className="mt-1 flex gap-3 text-xs text-gray-500">
              <span className="text-blue-600">● {statusSummary.programado} programados</span>
              <span className="text-green-600">● {statusSummary.publicado} publicados</span>
              {statusSummary.fallido > 0 && <span className="text-red-600">● {statusSummary.fallido} fallidos</span>}
            </div>
          )}
        </div>
        <select
          value={clienteId}
          onChange={(e) => setClienteId(e.target.value)}
          className="rounded-xl border border-gray-200 px-4 py-2 text-sm focus:border-brand focus:outline-none"
        >
          <option value="">Selecciona un cliente</option>
          {clientes.map((c) => (
            <option key={c.id} value={c.id}>@{c.instagram_username} — {c.name}</option>
          ))}
        </select>
      </div>

      {/* Navegación de mes */}
      <div className="mb-4 flex items-center gap-4">
        <button onClick={() => navMes(-1)}
          className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm hover:bg-gray-50">←</button>
        <span className="text-lg font-semibold text-gray-900 min-w-[160px] text-center">
          {MESES[month]} {year}
        </span>
        <button onClick={() => navMes(1)}
          className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm hover:bg-gray-50">→</button>
        <button
          onClick={() => { setYear(now.getFullYear()); setMonth(now.getMonth()); }}
          className="ml-2 rounded-lg border border-gray-200 px-3 py-1.5 text-xs text-gray-500 hover:bg-gray-50"
        >
          Hoy
        </button>
        {loading && <span className="text-xs text-gray-400 animate-pulse">Cargando...</span>}
      </div>

      {!clienteId ? (
        <div className="rounded-xl border-2 border-dashed border-gray-200 py-16 text-center">
          <p className="text-sm text-gray-500">Selecciona un cliente para ver su calendario.</p>
        </div>
      ) : (
        <CalendarGrid
          year={year}
          month={month}
          posts={posts}
          onPostClick={setEditandoPost}
        />
      )}

      {editandoPost && (
        <PostEditModal
          post={editandoPost}
          onClose={() => setEditandoPost(null)}
          onUpdated={handlePostUpdated}
        />
      )}
    </div>
  );
}
