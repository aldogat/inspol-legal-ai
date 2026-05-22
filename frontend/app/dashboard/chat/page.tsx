"use client";
import { useEffect, useState, useRef } from "react";
import { apiFetch } from "@/app/lib/api";
import { Trash2, Send } from "lucide-react";
import moment from "moment";
import "moment/locale/es";

const API = "http://localhost:8000/api/v1";

export default function ChatPage() {
  const [mensajes, setMensajes] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    fetchHistorial();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [mensajes]);

  const fetchHistorial = async () => {
    try {
      const res = await apiFetch(`${API}/chat/historial`);
      if (!res.ok) throw new Error("Error al cargar historial");
      const data = await res.json();
      setMensajes(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setError("");
    // Agregar mensaje del usuario optimistamente
    const tempUserMsg = { id: Date.now(), rol: "user", contenido: input, created_at: new Date().toISOString() };
    setMensajes((prev) => [...prev, tempUserMsg]);
    setInput("");
    try {
      const res = await apiFetch(`${API}/chat/multimodal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ consulta: tempUserMsg.contenido }),
      });
      if (!res.ok) throw new Error("Error al enviar mensaje");
      const data = await res.json();
      // Agregar respuesta del asistente
      const assistantMsg = { id: Date.now() + 1, rol: "assistant", contenido: data.respuesta, created_at: new Date().toISOString() };
      setMensajes((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    if (!confirm("¿Borrar todo el historial?")) return;
    try {
      await apiFetch(`${API}/chat/historial`, { method: "DELETE" });
      setMensajes([]);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="p-6 flex flex-col h-[calc(100vh-6rem)]">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold">Chat IA</h1>
        <button onClick={handleClear} className="flex items-center gap-2 bg-red-600/20 hover:bg-red-600/40 px-4 py-2 rounded-lg text-red-400 transition">
          <Trash2 size={18} />
          Borrar historial
        </button>
      </div>

      {error && <p className="text-red-400 mb-4">{error}</p>}

      <div className="flex-1 overflow-y-auto space-y-4 mb-4 bg-white/5 border border-white/10 rounded-2xl p-4">
        {mensajes.length === 0 && (
          <p className="text-gray-400 text-center mt-8">No hay conversaciones aún. ¡Empieza a chatear!</p>
        )}
        {mensajes.map((msg) => (
          <div key={msg.id} className={`flex ${msg.rol === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[70%] rounded-2xl px-4 py-3 ${
              msg.rol === "user"
                ? "bg-blue-600 text-white"
                : "bg-white/10 text-gray-200"
            }`}>
              <p className="whitespace-pre-wrap">{msg.contenido}</p>
              <p className="text-xs mt-1 opacity-60">{moment(msg.created_at).format("LT")}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white/10 rounded-2xl px-4 py-3">
              <span className="animate-pulse">Pensando...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Escribe tu consulta legal..."
          className="flex-1 bg-white/10 border border-white/10 rounded-xl p-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="bg-blue-600 hover:bg-blue-500 px-6 py-3 rounded-xl disabled:opacity-50 transition flex items-center gap-2"
        >
          <Send size={18} />
          Enviar
        </button>
      </div>
    </div>
  );
}
