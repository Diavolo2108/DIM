"use client";

import { useState, useEffect, useCallback } from "react";
import { apiFetch } from "@/lib/api";

interface Cliente { id: string; name: string; instagram_username: string; }
interface AutoReply {
  id: string; client_id: string; is_active: boolean;
  system_prompt: string | null; delay_seconds: number;
}
interface Mensaje {
  id: string; client_id: string; instagram_thread_id: string;
  sender_id: string; sender_username: string | null; content: string;
  type: "DM" | "COMMENT"; is_from_page: boolean;
  replied: boolean; received_at: string;
}

type FiltroTipo = "ALL" | "DM" | "COMMENT";
type FiltroLeido = "ALL" | "UNREAD";

const TYPE_LABELS: Record<string, string> = { DM: "DM", COMMENT: "Comentario" };
const TYPE_COLORS: Record<string, string> = {
  DM: "bg-blue-100 text-blue-700",
  COMMENT: "bg-purple-100 text-purple-700",
};

function formatFecha(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString("es", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
}

export default function InboxPage() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [clienteId, setClienteId] = useState("");
  const [mensajes, setMensajes] = useState<Mensaje[]>([]);
  const [filtroTipo, setFiltroTipo] = useState<FiltroTipo>("ALL");
  const [filtroLeido, setFiltroLeido] = useState<FiltroLeido>("ALL");
  const [loading, setLoading] = useState(false);
  const [sincronizando, setSincronizando] = useState(false);
  const [autoReply, setAutoReply] = useState<AutoReply | null>(null);
  const [showArConfig, setShowArConfig] = useState(false);
  const [arPrompt, setArPrompt] = useState("");
  const [respondiendo, setRespondiendo] = useState<string | null>(null);
  const [textoRespuesta, setTextoRespuesta] = useState("");
  const [enviando, setEnviando] = useState(false);

  useEffect(() => { apiFetch("/clients/").then(setClientes).catch(() => {}); }, []);

  useEffect(() => {
    if (!clienteId) { setAutoReply(null); return; }
    apiFetch(`/auto-replies/${clienteId}`)
      .then((ar) => { setAutoReply(ar); setArPrompt(ar.system_prompt ?? ""); })
      .catch(() => setAutoReply(null));
  }, [clienteId]);

  async function handleToggleAutoReply() {
    if (!clienteId) return;
    try {
      if (!autoReply) {
        const ar = await apiFetch(`/auto-replies/${clienteId}`, {
          method: "PUT",
          body: JSON.stringify({ is_active: true, system_prompt: arPrompt, delay_seconds: 0 }),
        });
        setAutoReply(ar);
      } else {
        const ar = await apiFetch(`/auto-replies/${clienteId}/toggle`, { method: "PATCH" });
        setAutoReply(ar);
      }
    } catch (e: any) { alert(e.message); }
  }

  async function handleGuardarPrompt() {
    if (!clienteId) return;
    try {
      const ar = await apiFetch(`/auto-replies/${clienteId}`, {
        method: "PUT",
        body: JSON.stringify({ is_active: autoReply?.is_active ?? false, system_prompt: arPrompt, delay_seconds: 0 }),
      });
      setAutoReply(ar);
      setShowArConfig(false);
    } catch (e: any) { alert(e.message); }
  }

  const cargarMensajes = useCallback(async () => {
    if (!clienteId) { setMensajes([]); return; }
    setLoading(true);
    try {
      const params = new URLSearchParams({ client_id: clienteId });
      if (filtroTipo !== "ALL") params.append("type", filtroTipo);
      if (filtroLeido === "UNREAD") params.append("replied", "false");
      const data = await apiFetch(`/messages/?${params}`);
      setMensajes(data);
    } catch { setMensajes([]); }
    finally { setLoading(false); }
  }, [clienteId, filtroTipo, filtroLeido]);

  useEffect(() => { cargarMensajes(); }, [cargarMensajes]);

  async function handleSincronizar() {
    if (!clienteId) return;
    setSincronizando(true);
    try {
      const data = await apiFetch(`/messages/sync?client_id=${clienteId}`, { method: "POST" });
      if (data.nuevos > 0) cargarMensajes();
      alert(`Sincronización completada: ${data.nuevos} mensajes nuevos`);
    } catch (e: any) { alert(e.message); }
    finally { setSincronizando(false); }
  }

  async function handleResponder(msgId: string) {
    if (!textoRespuesta.trim()) return;
    setEnviando(true);
    try {
      const updated = await apiFetch(`/messages/${msgId}/reply`, {
        method: "POST",
        body: JSON.stringify({ content: textoRespuesta }),
      });
      setMensajes((prev) => prev.map((m) => m.id === msgId ? { ...m, replied: true } : m));
      setRespondiendo(null);
      setTextoRespuesta("");
    } catch (e: any) { alert(e.message); }
    finally { setEnviando(false); }
  }

  const sinLeer = mensajes.filter((m) => !m.replied && !m.is_from_page).length;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inbox</h1>
          {sinLeer > 0 && (
            <span className="mt-1 inline-block rounded-full bg-brand px-2 py-0.5 text-xs text-white">
              {sinLeer} sin responder
            </span>
          )}
        </div>
        <div className="flex gap-3">
          <select value={clienteId} onChange={(e) => setClienteId(e.target.value)}
            className="rounded-xl border border-gray-200 px-4 py-2 text-sm focus:border-brand focus:outline-none">
            <option value="">Selecciona un cliente</option>
            {clientes.map((c) => (
              <option key={c.id} value={c.id}>@{c.instagram_username}</option>
            ))}
          </select>
          {clienteId && autoReply !== undefined && (
            <button
              onClick={handleToggleAutoReply}
              className={`rounded-xl px-3 py-2 text-xs font-medium border ${autoReply?.is_active ? "border-green-300 bg-green-50 text-green-700" : "border-gray-200 text-gray-500 hover:bg-gray-50"}`}
            >
              {autoReply?.is_active ? "🤖 IA activa" : "🤖 IA desactivada"}
            </button>
          )}
          {clienteId && autoReply?.is_active && (
            <button onClick={() => setShowArConfig(!showArConfig)}
              className="rounded-xl border border-gray-200 px-3 py-2 text-xs text-gray-500 hover:bg-gray-50">
              ⚙ Configurar
            </button>
          )}
          {clienteId && (
            <button onClick={handleSincronizar} disabled={sincronizando}
              className="rounded-xl border border-gray-200 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50">
              {sincronizando ? "Sincronizando..." : "↻ Sincronizar"}
            </button>
          )}
        </div>
      </div>

      {/* Config autorrespuesta */}
      {showArConfig && (
        <div className="mb-4 rounded-xl border border-gray-200 bg-white p-4">
          <p className="mb-2 text-xs font-medium text-gray-700">Instrucciones para la IA (system prompt)</p>
          <textarea value={arPrompt} onChange={(e) => setArPrompt(e.target.value)} rows={3}
            className="w-full resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
            placeholder="Eres el asistente de atención al cliente de esta cuenta..." />
          <div className="mt-2 flex gap-2">
            <button onClick={handleGuardarPrompt}
              className="rounded-lg bg-brand px-4 py-1.5 text-xs font-medium text-white hover:bg-brand-dark">
              Guardar
            </button>
            <button onClick={() => setShowArConfig(false)}
              className="rounded-lg border border-gray-200 px-4 py-1.5 text-xs text-gray-600">
              Cancelar
            </button>
          </div>
        </div>
      )}

      {/* Filtros */}
      {clienteId && (
        <div className="mb-4 flex gap-2">
          {(["ALL", "DM", "COMMENT"] as FiltroTipo[]).map((t) => (
            <button key={t} onClick={() => setFiltroTipo(t)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium ${filtroTipo === t ? "bg-brand text-white" : "border border-gray-200 text-gray-600 hover:bg-gray-50"}`}>
              {t === "ALL" ? "Todos" : TYPE_LABELS[t]}
            </button>
          ))}
          <button onClick={() => setFiltroLeido(filtroLeido === "ALL" ? "UNREAD" : "ALL")}
            className={`ml-2 rounded-lg px-3 py-1.5 text-xs font-medium ${filtroLeido === "UNREAD" ? "bg-brand text-white" : "border border-gray-200 text-gray-600 hover:bg-gray-50"}`}>
            Sin responder
          </button>
        </div>
      )}

      {loading ? (
        <p className="text-sm text-gray-400">Cargando mensajes...</p>
      ) : !clienteId ? (
        <div className="rounded-xl border-2 border-dashed border-gray-200 py-16 text-center">
          <p className="text-sm text-gray-500">Selecciona un cliente para ver su inbox.</p>
        </div>
      ) : mensajes.length === 0 ? (
        <p className="text-sm text-gray-400">No hay mensajes con los filtros actuales.</p>
      ) : (
        <div className="space-y-2">
          {mensajes.map((m) => (
            <div key={m.id}
              className={`rounded-xl bg-white p-4 shadow-sm ${!m.replied && !m.is_from_page ? "border-l-4 border-brand" : ""}`}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="mb-1 flex items-center gap-2">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${TYPE_COLORS[m.type]}`}>
                      {TYPE_LABELS[m.type]}
                    </span>
                    <span className="text-xs font-medium text-gray-700">
                      {m.is_from_page ? "📤 Enviado" : `@${m.sender_username ?? m.sender_id}`}
                    </span>
                    <span className="text-xs text-gray-400">{formatFecha(m.received_at)}</span>
                    {m.replied && !m.is_from_page && (
                      <span className="text-xs text-green-600">✓ Respondido</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-800">{m.content}</p>
                </div>
                {!m.replied && !m.is_from_page && (
                  <button onClick={() => { setRespondiendo(m.id); setTextoRespuesta(""); }}
                    className="shrink-0 rounded-lg bg-brand px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-dark">
                    Responder
                  </button>
                )}
              </div>

              {respondiendo === m.id && (
                <div className="mt-3 flex gap-2">
                  <input type="text" value={textoRespuesta}
                    onChange={(e) => setTextoRespuesta(e.target.value)}
                    placeholder="Escribe tu respuesta..."
                    className="flex-1 rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
                    onKeyDown={(e) => { if (e.key === "Enter") handleResponder(m.id); }}
                  />
                  <button onClick={() => handleResponder(m.id)} disabled={enviando || !textoRespuesta.trim()}
                    className="rounded-lg bg-brand px-4 py-2 text-xs font-medium text-white disabled:opacity-40">
                    {enviando ? "..." : "Enviar"}
                  </button>
                  <button onClick={() => setRespondiendo(null)}
                    className="rounded-lg border border-gray-200 px-3 py-2 text-xs text-gray-500">✕</button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
