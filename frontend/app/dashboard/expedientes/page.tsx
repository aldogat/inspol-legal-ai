"use client";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { motion } from "framer-motion";
import { Pencil, Trash2, X, Paperclip, ChevronLeft, ChevronRight, History } from "lucide-react";
import { apiFetch } from "@/app/lib/api";
import toast from "react-hot-toast";
import { TableSkeleton } from "@/app/components/Skeleton";

const API = "http://localhost:8000/api/v1";
const PAGE_SIZE = 10;

export default function ExpedientesPage() {
  const [expedientes, setExpedientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [historialOpen, setHistorialOpen] = useState(false);
  const [historial, setHistorial] = useState([]);
  const [numSeleccionado, setNumSeleccionado] = useState("");
  const [page, setPage] = useState(0);
  const { register, handleSubmit, reset, setValue } = useForm();

  useEffect(() => { fetchExpedientes(); }, [page]);

  const fetchExpedientes = async () => {
    setLoading(true);
    try {
      const r = await apiFetch(`${API}/expedientes/?skip=${page * PAGE_SIZE}&limit=${PAGE_SIZE}`);
      if (!r.ok) throw new Error("Error");
      setExpedientes(await r.json());
    } catch (e: any) { toast.error(e.message); }
    finally { setLoading(false); }
  };

  const fetchHistorial = async (num: string) => {
    try {
      const r = await apiFetch(`${API}/historial/expedientes/${num}`);
      setHistorial(await r.json());
      setNumSeleccionado(num);
      setHistorialOpen(true);
    } catch (e: any) { toast.error(e.message); }
  };

  const onSubmit = async (fd: any) => {
    setSaving(true);
    try {
      const url = editingId ? `${API}/expedientes/${editingId}` : `${API}/expedientes/`;
      const res = await apiFetch(url, { method: editingId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(fd) });
      if (!res.ok) throw new Error((await res.json()).detail || "Error");
      toast.success(editingId ? "Actualizado" : "Creado");
      fetchExpedientes(); setModalOpen(false);
    } catch (e: any) { toast.error(e.message); }
    finally { setSaving(false); }
  };

  const deleteExpediente = async (id: number) => {
    if (!confirm("¿Eliminar?")) return;
    try { await apiFetch(`${API}/expedientes/${id}`, { method: "DELETE" }); toast.success("Eliminado"); fetchExpedientes(); }
    catch (e: any) { toast.error(e.message); }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Expedientes</h1>
        <button onClick={() => { reset({}); setEditingId(null); setModalOpen(true); }} className="bg-gray-900 dark:bg-white text-white dark:text-gray-900 px-4 py-2 rounded-lg text-sm font-medium">+ Nuevo</button>
      </div>

      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
        {loading ? <TableSkeleton rows={5} cols={6} /> : (
          <table className="w-full text-sm">
            <thead><tr className="text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700"><th className="text-left p-3">Número</th><th className="text-left p-3">Cliente</th><th className="text-left p-3">Estado</th><th className="text-left p-3">Prioridad</th><th className="text-left p-3">Historial</th><th className="text-left p-3">Acciones</th></tr></thead>
            <tbody>
              {expedientes.map((exp: any) => (
                <tr key={exp.id} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td className="p-3 font-medium text-gray-900 dark:text-white">{exp.numero_expediente}</td>
                  <td className="p-3 text-gray-700 dark:text-gray-300">{exp.cliente}</td>
                  <td className="p-3"><span className="bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300 px-2 py-0.5 rounded text-xs">{exp.estado}</span></td>
                  <td className="p-3"><span className={`px-2 py-0.5 rounded text-xs ${exp.prioridad==="Alta"?"bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300":"bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300"}`}>{exp.prioridad}</span></td>
                  <td className="p-3"><button onClick={() => fetchHistorial(exp.numero_expediente)} className="text-gray-500 hover:text-blue-600"><History size={16} /></button></td>
                  <td className="p-3">
                    <button onClick={() => { setEditingId(exp.id); setValue("numero_expediente", exp.numero_expediente); setValue("cliente", exp.cliente); setValue("estado", exp.estado); setValue("prioridad", exp.prioridad); setValue("descripcion", exp.descripcion||""); setValue("fecha_apertura", exp.fecha_apertura); setModalOpen(true); }} className="text-gray-500 hover:text-blue-600 mr-2"><Pencil size={16} /></button>
                    <button onClick={() => deleteExpediente(exp.id)} className="text-gray-500 hover:text-red-600"><Trash2 size={16} /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="flex items-center justify-between mt-4">
        <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} className="p-2 rounded-lg border border-gray-300 dark:border-gray-600 disabled:opacity-30"><ChevronLeft size={16} /></button>
        <span className="text-sm text-gray-500">Página {page + 1}</span>
        <button onClick={() => setPage(p => p + 1)} disabled={expedientes.length < PAGE_SIZE} className="p-2 rounded-lg border border-gray-300 dark:border-gray-600 disabled:opacity-30"><ChevronRight size={16} /></button>
      </div>

      {modalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md shadow-xl">
            <div className="flex justify-between items-center mb-4"><h2 className="text-lg font-bold text-gray-900 dark:text-white">{editingId?"Editar":"Nuevo"}</h2><button onClick={() => setModalOpen(false)}><X size={20} className="text-gray-500" /></button></div>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
              <input {...register("numero_expediente")} placeholder="Número*" className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white placeholder-gray-400" required />
              <input {...register("cliente")} placeholder="Cliente*" className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white placeholder-gray-400" required />
              <input {...register("estado")} placeholder="Estado" className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white placeholder-gray-400" />
              <input {...register("prioridad")} placeholder="Prioridad" className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white placeholder-gray-400" />
              <textarea {...register("descripcion")} placeholder="Descripción" rows={2} className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white placeholder-gray-400" />
              <input {...register("fecha_apertura")} type="date" className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white" required />
              <button type="submit" disabled={saving} className="w-full bg-gray-900 dark:bg-white text-white dark:text-gray-900 py-2 rounded-lg text-sm font-medium">{saving?"Guardando...":"Guardar"}</button>
            </form>
          </motion.div>
        </div>
      )}

      {historialOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-lg shadow-xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4"><h2 className="text-lg font-bold text-gray-900 dark:text-white">Historial: {numSeleccionado}</h2><button onClick={() => setHistorialOpen(false)}><X size={20} className="text-gray-500" /></button></div>
            {historial.length === 0 ? <p className="text-gray-500 dark:text-gray-400 text-sm">Sin movimientos</p> : (
              <div className="space-y-2">
                {historial.map((h: any) => (
                  <div key={h.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
                    <div className="flex justify-between items-center">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        h.accion === "creado" ? "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300" :
                        h.accion === "editado" ? "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300" :
                        "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300"
                      }`}>{h.accion}</span>
                      <span className="text-xs text-gray-500">{new Date(h.created_at).toLocaleString("es-MX")}</span>
                    </div>
                    {h.descripcion && <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{h.descripcion}</p>}
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        </div>
      )}
    </div>
  );
}
