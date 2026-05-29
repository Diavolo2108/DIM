"use client";

import { useState, useRef, DragEvent } from "react";
import { getSession } from "next-auth/react";

interface Props {
  clientId: string;
  campaignId?: string;
  onUploaded: (asset: any) => void;
}

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
const TIPOS_ACEPTADOS = ["image/jpeg", "image/png", "image/gif", "image/webp", "video/mp4", "video/quicktime", "video/x-msvideo"];

export function AssetUploader({ clientId, campaignId, onUploaded }: Props) {
  const [dragging, setDragging] = useState(false);
  const [subiendo, setSubiendo] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  async function subirArchivo(file: File) {
    if (!TIPOS_ACEPTADOS.includes(file.type)) {
      setError(`Tipo no permitido: ${file.type}`);
      return;
    }
    setError("");
    setSubiendo(true);

    try {
      const session = await getSession();
      const token = (session as any)?.accessToken;

      const form = new FormData();
      form.append("file", file);
      form.append("client_id", clientId);
      if (campaignId) form.append("campaign_id", campaignId);

      const res = await fetch(`${BACKEND}/assets/upload`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: form,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail);
      }
      onUploaded(await res.json());
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSubiendo(false);
    }
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) subirArchivo(file);
  }

  return (
    <div>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer rounded-xl border-2 border-dashed p-10 text-center transition-colors ${
          dragging ? "border-brand bg-pink-50" : "border-gray-200 hover:border-brand hover:bg-gray-50"
        }`}
      >
        <p className="text-sm font-medium text-gray-600">
          {subiendo ? "Subiendo..." : "Arrastra tu imagen o video aquí"}
        </p>
        <p className="mt-1 text-xs text-gray-400">JPG, PNG, WebP, GIF, MP4 · Máx. 100 MB</p>
        {!subiendo && (
          <span className="mt-3 inline-block rounded-lg bg-brand px-4 py-1.5 text-xs font-medium text-white">
            Seleccionar archivo
          </span>
        )}
      </div>
      <input
        ref={inputRef}
        type="file"
        accept={TIPOS_ACEPTADOS.join(",")}
        className="hidden"
        onChange={(e) => { const f = e.target.files?.[0]; if (f) subirArchivo(f); e.target.value = ""; }}
      />
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  );
}
