"use client";

import { useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";
import { AssetUploader } from "@/components/AssetUploader";
import { CopyGenerator } from "@/components/CopyGenerator";

interface Cliente { id: string; name: string; instagram_username: string; }
interface Campana { id: string; name: string; client_id: string; }
interface Asset {
  id: string; client_id: string; campaign_id: string | null;
  filename: string; content_type: string; r2_url: string; size_bytes: number;
}

type Tab = "assets" | "copies";

function formatBytes(b: number) {
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`;
  return `${(b / 1024 / 1024).toFixed(1)} MB`;
}

export default function ContenidoPage() {
  const [tab, setTab] = useState<Tab>("assets");
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [campanas, setCampanas] = useState<Campana[]>([]);
  const [clienteId, setClienteId] = useState("");
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    apiFetch("/clients/").then(setClientes).catch(() => {});
    apiFetch("/campaigns/").then(setCampanas).catch(() => {});
  }, []);

  useEffect(() => {
    if (!clienteId) { setAssets([]); return; }
    setLoading(true);
    apiFetch(`/assets/?client_id=${clienteId}`)
      .then(setAssets).catch(() => {}).finally(() => setLoading(false));
  }, [clienteId]);

  async function handleEliminar(id: string) {
    if (!confirm("¿Eliminar este asset?")) return;
    await apiFetch(`/assets/${id}`, { method: "DELETE" }).catch(() => {});
    setAssets((prev) => prev.filter((a) => a.id !== id));
  }

  const isImage = (ct: string) => ct.startsWith("image/");

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Contenido</h1>
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-xl bg-gray-100 p-1 w-fit">
        {(["assets", "copies"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              tab === t ? "bg-white text-gray-900 shadow-sm" : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {t === "assets" ? "Assets" : "Generar copies"}
          </button>
        ))}
      </div>

      {tab === "assets" && (
        <div>
          <div className="mb-6">
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

          {clienteId && (
            <div className="mb-8">
              <AssetUploader clientId={clienteId} onUploaded={(a) => setAssets((p) => [a, ...p])} />
            </div>
          )}

          {loading ? (
            <p className="text-sm text-gray-400">Cargando assets...</p>
          ) : assets.length > 0 ? (
            <div>
              <p className="mb-3 text-xs font-medium uppercase tracking-wide text-gray-500">{assets.length} assets</p>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                {assets.map((a) => (
                  <div key={a.id} className="group relative overflow-hidden rounded-xl bg-white shadow">
                    {isImage(a.content_type) ? (
                      <img src={a.r2_url} alt={a.filename} className="h-36 w-full object-cover"
                        onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
                    ) : (
                      <div className="flex h-36 items-center justify-center bg-gray-100 text-3xl">🎬</div>
                    )}
                    <div className="p-2">
                      <p className="truncate text-xs font-medium text-gray-700">{a.filename}</p>
                      <p className="text-xs text-gray-400">{formatBytes(a.size_bytes)}</p>
                    </div>
                    <button onClick={() => handleEliminar(a.id)}
                      className="absolute right-1 top-1 hidden rounded-lg bg-red-500 px-2 py-0.5 text-xs text-white group-hover:block">
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ) : clienteId ? (
            <p className="text-sm text-gray-400">No hay assets para este cliente aún.</p>
          ) : null}
        </div>
      )}

      {tab === "copies" && (
        <div className="max-w-xl">
          <CopyGenerator campanas={campanas} />
        </div>
      )}
    </div>
  );
}
