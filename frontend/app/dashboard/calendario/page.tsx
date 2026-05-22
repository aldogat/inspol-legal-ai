"use client";
import { useEffect, useState, useCallback } from "react";
import { Calendar, momentLocalizer, Views } from "react-big-calendar";
import moment from "moment";
import "react-big-calendar/lib/css/react-big-calendar.css";
import { useForm } from "react-hook-form";
import { motion, AnimatePresence } from "framer-motion";
import { X, Plus } from "lucide-react";
import { apiFetch } from "@/app/lib/api";
import "./calendario.css";

moment.locale("es");
const localizer = momentLocalizer(moment);

const API = "http://localhost:8000/api/v1";

export default function CalendarioPage() {
  const [eventos, setEventos] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const { register, handleSubmit, reset, setValue } = useForm();

  useEffect(() => {
    fetchEventos();
  }, []);

  const fetchEventos = async () => {
    try {
      const res = await apiFetch(`${API}/eventos/`);
      if (!res.ok) throw new Error("Error al cargar eventos");
      const data = await res.json();
      const formatted = data.map((ev: any) => ({
        ...ev,
        start: new Date(ev.fecha_inicio),
        end: new Date(ev.fecha_fin),
        title: ev.titulo,
      }));
      setEventos(formatted);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const openNewModal = () => {
    reset({ tipo: "Reunión", color: "#3b82f6" });
    setEditingId(null);
    setModalOpen(true);
  };

  const openEditModal = (evento: any) => {
    setEditingId(evento.id);
    setValue("titulo", evento.titulo);
    setValue("descripcion", evento.descripcion || "");
    setValue("fecha_inicio", moment(evento.start).format("YYYY-MM-DDTHH:mm"));
    setValue("fecha_fin", moment(evento.end).format("YYYY-MM-DDTHH:mm"));
    setValue("tipo", evento.tipo);
    setValue("ubicacion", evento.ubicacion || "");
    setValue("color", evento.color);
    setModalOpen(true);
  };

  const closeModal = () => setModalOpen(false);

  const onSubmit = async (formData: any) => {
    setError("");
    const payload = {
      ...formData,
      fecha_inicio: new Date(formData.fecha_inicio).toISOString(),
      fecha_fin: new Date(formData.fecha_fin).toISOString(),
    };
    try {
      const url = editingId ? `${API}/eventos/${editingId}` : `${API}/eventos/`;
      const method = editingId ? "PUT" : "POST";
      const res = await apiFetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Error al guardar");
      }
      await fetchEventos();
      closeModal();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const deleteEvento = async (id: number) => {
    if (!confirm("¿Eliminar evento?")) return;
    try {
      await apiFetch(`${API}/eventos/${id}`, { method: "DELETE" });
      setEventos((prev) => prev.filter((ev) => ev.id !== id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  const eventStyleGetter = (event: any) => {
    const backgroundColor = event.color || "#3b82f6";
    return {
      style: {
        backgroundColor,
        borderRadius: "4px",
        opacity: 0.8,
        color: "white",
        border: "none",
        padding: "2px 5px",
      },
    };
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Calendario</h1>
        <button onClick={openNewModal} className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg flex items-center gap-2">
          <Plus size={18} /> Nuevo Evento
        </button>
      </div>
      {error && <p className="text-red-400 mb-4">{error}</p>}
      <div className="bg-[#0b1020] rounded-xl p-4 border border-white/10" style={{ height: "75vh" }}>
        <Calendar
          localizer={localizer}
          events={eventos}
          startAccessor="start"
          endAccessor="end"
          defaultView={Views.MONTH}
          views={[Views.MONTH, Views.WEEK, Views.DAY]}
          style={{ height: "100%", color: "white" }}
          eventPropGetter={eventStyleGetter}
          onSelectEvent={(e) => openEditModal(e)}
          selectable
          onSelectSlot={openNewModal}
          messages={{
            today: "Hoy",
            previous: "Anterior",
            next: "Siguiente",
            month: "Mes",
            week: "Semana",
            day: "Día",
          }}
        />
      </div>
      <AnimatePresence>
        {modalOpen && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
            <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} exit={{ scale: 0.9 }} className="bg-[#0b1020] border border-white/10 rounded-2xl p-6 w-full max-w-md">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">{editingId ? "Editar" : "Nuevo"} Evento</h2>
                <button onClick={closeModal}><X /></button>
              </div>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <input {...register("titulo")} placeholder="Título*" className="w-full bg-white/10 border border-white/10 rounded-lg p-2 text-white" required />
                <textarea {...register("descripcion")} placeholder="Descripción" rows={2} className="w-full bg-white/10 border border-white/10 rounded-lg p-2 text-white" />
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-white/60">Inicio</label>
                    <input {...register("fecha_inicio")} type="datetime-local" className="w-full bg-white/10 border border-white/10 rounded-lg p-2 mt-1 text-white" required />
                  </div>
                  <div>
                    <label className="text-sm text-white/60">Fin</label>
                    <input {...register("fecha_fin")} type="datetime-local" className="w-full bg-white/10 border border-white/10 rounded-lg p-2 mt-1 text-white" required />
                  </div>
                </div>
                <select {...register("tipo")} className="w-full bg-white/10 border border-white/10 rounded-lg p-2 text-white">
                  <option value="Audiencia">Audiencia</option>
                  <option value="Reunión">Reunión</option>
                  <option value="Plazo">Plazo</option>
                  <option value="Otro">Otro</option>
                </select>
                <input {...register("ubicacion")} placeholder="Ubicación" className="w-full bg-white/10 border border-white/10 rounded-lg p-2 text-white" />
                <input {...register("color")} type="color" className="w-full h-10 bg-white/10 border border-white/10 rounded-lg p-1" />
                <div className="flex gap-2">
                  <button type="submit" className="flex-1 bg-blue-600 py-2 rounded-xl hover:bg-blue-500 text-white">Guardar</button>
                  {editingId && (
                    <button type="button" onClick={() => deleteEvento(editingId)} className="px-4 py-2 bg-red-600 rounded-xl hover:bg-red-500 text-white">Eliminar</button>
                  )}
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
