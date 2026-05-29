"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ChatMessage } from "@/components/chat/ChatMessage";
import { ChatInput } from "@/components/chat/ChatInput";
import { apiFetch } from "@/lib/api";

interface Mensaje {
  role: "user" | "assistant";
  content: string;
}

interface Cliente {
  id: string;
  name: string;
  instagram_username: string;
}

const MENSAJE_INICIAL: Mensaje = {
  role: "assistant",
  content:
    "Hola, soy tu asistente de planificación de campañas. Para empezar, cuéntame:\n\n" +
    "¿Para qué cliente es esta campaña y cuál es su objetivo principal?\n" +
    "(Ej: aumentar seguidores, promocionar un servicio, mejorar engagement, etc.)",
};

export default function NuevaCampanaPage() {
  const router = useRouter();
  const [mensajes, setMensajes] = useState<Mensaje[]>([MENSAJE_INICIAL]);
  const [historial, setHistorial] = useState<{ role: string; content: string }[]>([]);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [clienteSeleccionado, setClienteSeleccionado] = useState("");
  const [nombreCampana, setNombreCampana] = useState("");
  const [cargando, setCargando] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [planListo, setPlanListo] = useState(false);
  const [campanaGuardada, setCampanaGuardada] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    apiFetch("/clients/").then(setClientes).catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [mensajes, cargando]);

  const clienteActual = clientes.find((c) => c.id === clienteSeleccionado);

  async function handleEnviar(mensaje: string) {
    const nuevosMensajes: Mensaje[] = [...mensajes, { role: "user", content: mensaje }];
    setMensajes(nuevosMensajes);
    setCargando(true);

    try {
      const data = await apiFetch("/campaigns/plan", {
        method: "POST",
        body: JSON.stringify({
          message: mensaje,
          historial,
          contexto_cliente: clienteActual
            ? `@${clienteActual.instagram_username} — ${clienteActual.name}`
            : undefined,
        }),
      });

      setHistorial(data.historial_actualizado);
      setMensajes([...nuevosMensajes, { role: "assistant", content: data.respuesta }]);

      const r = data.respuesta.toLowerCase();
      if ((r.includes("|") || r.includes("semana") || r.includes("calendario")) && data.historial_actualizado.length >= 4) {
        setPlanListo(true);
      }
    } catch (e: any) {
      setMensajes([...nuevosMensajes, { role: "assistant", content: `Error: ${e.message}` }]);
    } finally {
      setCargando(false);
    }
  }

  async function handleGuardar() {
    if (!clienteSeleccionado) { alert("Selecciona un cliente antes de guardar"); return; }
    if (!nombreCampana.trim()) { alert("Escribe un nombre para la campaña"); return; }
    setGuardando(true);
    try {
      const data = await apiFetch("/campaigns/", {
        method: "POST",
        body: JSON.stringify({
          client_id: clienteSeleccionado,
          name: nombreCampana,
          objetivo: historial.find((m) => m.role === "user")?.content ?? nombreCampana,
          historial,
        }),
      });
      setCampanaGuardada(data.id);
    } catch (e: any) {
      alert(`Error al guardar: ${e.message}`);
    } finally {
      setGuardando(false);
    }
  }

  if (campanaGuardada) {
    return (
      <div className="flex h-[calc(100vh-8rem)] flex-col items-center justify-center gap-4">
        <div className="rounded-full bg-green-100 p-6 text-4xl">✅</div>
        <h2 className="text-xl font-bold text-gray-900">¡Campaña guardada!</h2>
        <p className="text-sm text-gray-500">
          Se generaron <code>contexto.md</code> y <code>aprobacion-cliente.md</code> en la carpeta del cliente.
        </p>
        <div className="flex gap-3">
          <button
            onClick={() => router.push("/dashboard/campanas")}
            className="rounded-lg bg-brand px-5 py-2 text-sm font-medium text-white hover:bg-brand-dark"
          >
            Ver campañas
          </button>
          <button
            onClick={() => router.push("/dashboard/clientes")}
            className="rounded-lg border border-gray-300 px-5 py-2 text-sm text-gray-700 hover:bg-gray-50"
          >
            Ir a clientes
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Nueva campaña</h1>
          <p className="text-sm text-gray-500">Planifica con ayuda de IA</p>
        </div>
        <div className="flex gap-3">
          {planListo && (
            <button
              onClick={handleGuardar}
              disabled={guardando}
              className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
            >
              {guardando ? "Guardando..." : "Guardar campaña →"}
            </button>
          )}
          <button
            onClick={() => router.back()}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50"
          >
            Cancelar
          </button>
        </div>
      </div>

      {/* Configuración inicial */}
      <div className="mb-3 flex gap-3">
        <select
          value={clienteSeleccionado}
          onChange={(e) => setClienteSeleccionado(e.target.value)}
          className="rounded-xl border border-gray-200 px-4 py-2 text-sm focus:border-brand focus:outline-none"
        >
          <option value="">Selecciona un cliente</option>
          {clientes.map((c) => (
            <option key={c.id} value={c.id}>@{c.instagram_username} — {c.name}</option>
          ))}
        </select>
        <input
          type="text"
          placeholder="Nombre de la campaña"
          value={nombreCampana}
          onChange={(e) => setNombreCampana(e.target.value)}
          className="flex-1 rounded-xl border border-gray-200 px-4 py-2 text-sm focus:border-brand focus:outline-none"
        />
      </div>

      {/* Chat */}
      <div className="flex-1 overflow-y-auto rounded-xl bg-gray-50 p-4 space-y-3">
        {mensajes.map((m, i) => (
          <ChatMessage key={i} role={m.role} content={m.content} />
        ))}
        {cargando && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-white px-4 py-3 text-sm text-gray-400 shadow-sm">
              Claude está pensando...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="mt-3">
        <ChatInput onSend={handleEnviar} disabled={cargando} />
      </div>
    </div>
  );
}
