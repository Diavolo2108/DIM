"use client";

import { useState } from "react";
import { CalendarPost } from "./types";
import { apiFetch } from "@/lib/api";

interface Props {
  post: CalendarPost;
  onClose: () => void;
  onUpdated: (post: CalendarPost) => void;
}

const FORMAT_OPTIONS = ["IMAGE", "CAROUSEL", "REEL"] as const;
const STATUS_OPTIONS = ["PROGRAMADO", "PUBLICADO", "FALLIDO"] as const;

export function PostEditModal({ post, onClose, onUpdated }: Props) {
  const local = new Date(post.scheduled_at);
  const toLocal = (d: Date) => {
    const pad = (n: number) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  };

  const [scheduledAt, setScheduledAt] = useState(toLocal(local));
  const [format, setFormat] = useState(post.format);
  const [caption, setCaption] = useState(post.caption ?? "");
  const [status, setStatus] = useState(post.status);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");

  async function handleGuardar(e: React.FormEvent) {
    e.preventDefault();
    setGuardando(true);
    setError("");
    try {
      const updated = await apiFetch(`/posts/${post.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          scheduled_at: new Date(scheduledAt).toISOString(),
          format,
          caption: caption || null,
          status,
        }),
      });
      onUpdated(updated);
      onClose();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setGuardando(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-sm rounded-xl bg-white p-6 shadow-xl">
        <h2 className="mb-4 text-base font-bold text-gray-900">Editar post</h2>
        <form onSubmit={handleGuardar} className="space-y-3">

          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">Fecha y hora</label>
            <input type="datetime-local" value={scheduledAt}
              onChange={(e) => setScheduledAt(e.target.value)} required
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand focus:outline-none" />
          </div>

          <div className="flex gap-3">
            <div className="flex-1">
              <label className="mb-1 block text-xs font-medium text-gray-600">Formato</label>
              <select value={format} onChange={(e) => setFormat(e.target.value as any)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand focus:outline-none">
                {FORMAT_OPTIONS.map((f) => <option key={f}>{f}</option>)}
              </select>
            </div>
            <div className="flex-1">
              <label className="mb-1 block text-xs font-medium text-gray-600">Estado</label>
              <select value={status} onChange={(e) => setStatus(e.target.value as any)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand focus:outline-none">
                {STATUS_OPTIONS.map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">Caption</label>
            <textarea value={caption} onChange={(e) => setCaption(e.target.value)} rows={3}
              placeholder="Caption del post (opcional)"
              className="w-full resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand focus:outline-none" />
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <div className="flex gap-3 pt-1">
            <button type="submit" disabled={guardando}
              className="flex-1 rounded-lg bg-brand py-2 text-sm font-medium text-white hover:bg-brand-dark disabled:opacity-50">
              {guardando ? "Guardando..." : "Guardar"}
            </button>
            <button type="button" onClick={onClose}
              className="flex-1 rounded-lg border border-gray-200 py-2 text-sm text-gray-700 hover:bg-gray-50">
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
