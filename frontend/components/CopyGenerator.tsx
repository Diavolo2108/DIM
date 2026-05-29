"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";

interface Campana { id: string; name: string; }

interface Props {
  campanas: Campana[];
}

type Formato = "IMAGE" | "CAROUSEL" | "REEL";

const FORMATOS: { value: Formato; label: string }[] = [
  { value: "IMAGE", label: "Imagen" },
  { value: "CAROUSEL", label: "Carrusel" },
  { value: "REEL", label: "Reel" },
];

export function CopyGenerator({ campanas }: Props) {
  const [campanaid, setCampanaid] = useState("");
  const [instruccion, setInstruccion] = useState("");
  const [formato, setFormato] = useState<Formato>("IMAGE");
  const [resultado, setResultado] = useState<{ caption: string; hashtags: string[] } | null>(null);
  const [generando, setGenerando] = useState(false);
  const [error, setError] = useState("");
  const [copiado, setCopiado] = useState(false);

  async function handleGenerar(e: React.FormEvent) {
    e.preventDefault();
    if (!campanaid || !instruccion.trim()) return;
    setGenerando(true);
    setError("");
    setResultado(null);
    try {
      const data = await apiFetch("/posts/generate-copy", {
        method: "POST",
        body: JSON.stringify({ campaign_id: campanaid, instruccion, formato }),
      });
      setResultado(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setGenerando(false);
    }
  }

  function handleCopiar() {
    if (!resultado) return;
    const hashtags = resultado.hashtags.map((h) => `#${h}`).join(" ");
    navigator.clipboard.writeText(`${resultado.caption}\n\n${hashtags}`);
    setCopiado(true);
    setTimeout(() => setCopiado(false), 2000);
  }

  return (
    <div className="rounded-xl bg-white p-6 shadow">
      <h2 className="mb-4 text-base font-bold text-gray-900">Generar copy con IA</h2>

      <form onSubmit={handleGenerar} className="space-y-3">
        <div className="flex gap-3">
          <select
            value={campanaid}
            onChange={(e) => setCampanaid(e.target.value)}
            required
            className="flex-1 rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
          >
            <option value="">Selecciona una campaña</option>
            {campanas.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          <select
            value={formato}
            onChange={(e) => setFormato(e.target.value as Formato)}
            className="rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
          >
            {FORMATOS.map((f) => (
              <option key={f.value} value={f.value}>{f.label}</option>
            ))}
          </select>
        </div>

        <textarea
          value={instruccion}
          onChange={(e) => setInstruccion(e.target.value)}
          required
          rows={2}
          placeholder="¿De qué trata este post? (Ej: presentar nuestro nuevo servicio de branding)"
          className="w-full resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-brand focus:outline-none"
        />

        <button
          type="submit"
          disabled={generando || !campanaid || !instruccion.trim()}
          className="w-full rounded-lg bg-brand py-2 text-sm font-medium text-white hover:bg-brand-dark disabled:opacity-40"
        >
          {generando ? "Generando..." : "Generar copy"}
        </button>
      </form>

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      {resultado && (
        <div className="mt-4 space-y-3">
          <div className="rounded-lg bg-gray-50 p-4">
            <p className="whitespace-pre-wrap text-sm text-gray-800">{resultado.caption}</p>
          </div>
          {resultado.hashtags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {resultado.hashtags.map((h) => (
                <span key={h} className="rounded-full bg-pink-50 px-2.5 py-0.5 text-xs text-brand font-medium">
                  #{h}
                </span>
              ))}
            </div>
          )}
          <button
            onClick={handleCopiar}
            className="w-full rounded-lg border border-gray-200 py-2 text-sm text-gray-700 hover:bg-gray-50"
          >
            {copiado ? "¡Copiado!" : "Copiar al portapapeles"}
          </button>
        </div>
      )}
    </div>
  );
}
