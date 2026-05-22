"use client";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { motion } from "framer-motion";
import { Pencil, Trash2, X, AlertTriangle, Sparkles, Upload } from "lucide-react";
import { apiFetch } from "@/app/lib/api";
import toast from "react-hot-toast";

const API = "http://localhost:8000/api/v1";

export default function ContratosPage() {
  const [contratos, setContratos] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [analisisModal, setAnalisisModal] = useState(false);
  const [analisisResult, setAnalisisResult] = useState("");
  const [analizando, setAnalizando] = useState(false);
  const { register, handleSubmit, reset, setValue } = useForm();

  useEffect(() => { fetchContratos(); fetchClientes(); }, []);

  const fetchContratos = async () => {
    try {
      const r = await apiFetch(`${API}/contratos/`);
      const data = await r.json();
      setContratos(Array.isArray(data) ? data : []);
    } catch (e: any) { toast.error("Error al cargar contratos"); }
  };

  const fetchClientes = async () => {
    try {
      const r = await apiFetch(`${API}/clientes/`);
      const data = await r.json();
      setClientes(Array.isArray(data) ? data : []);
    } catch (e: any) { toast.error("Error al cargar clientes"); }
  };

  const onSubmit = async (fd: any) => {
    setLoading(true);
    try {
      const url = editingId ? `${API}/contratos/${editingId}` : `${API}/contratos/`;
      const method = editingId ? "PUT" : "POST";
      const res = await apiFetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...fd, cliente_id: parseInt(fd.cliente_id) }),
      });
      if (!res.ok) throw new Error("Error al guardar");
      toast.success(editingId ? "Contrato actualizado" : "Contrato creado");
      fetchContratos();
      setModalOpen(false);
    } catch (e: any) { toast.error(e.message); }
    finally { setLoading(false); }
  };

  const deleteContrato = async (id: number) => {
    if (!confirm("¿Eliminar contrato?")) return;
    try {
      await apiFetch(`${API}/contratos/${id}`, { method: "DELETE" });
      toast.success("Contrato eliminado");
      fetchContratos();
    } catch (e: any) { toast.error("Error al eliminar"); }
  };

  const handleAnalizar = async (file: File) => {
    setAnalizando(true);
    setAnalisisResult("");
    setAnalisisModal(true);
    
    const fd = new FormData();
    fd.append("file", file);
    fd.append("tipo_analisis", "completo");
    
    try {
      const res = await apiFetch(`${API}/analisis/contrato`, {
        method: "POST",
        body: fd,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Error al analizar");
      }
      const data = await res.json();
      setAnalisisResult(data.analisis || "Análisis completado");
      toast.success("Contrato analizado con IA");
    } catch (e: any) {
      toast.error(e.message);
      setAnalisisResult("Error: " + e.message);
    } finally {
      setAnalizando(false);
    }
  };

  const hoy = new Date();
  const esProximo = (f: string) => {
    const v = new Date(f);
    const diff = (v.getTime() - hoy.getTime()) / (1000 * 60 * 60 * 24);
    return diff <= 30 && diff > 0;
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Contratos</h1>
        <div className="flex gap-3">
          <label className="bg-violet-600 hover:bg-violet-500 text-white px-4 py-2 rounded-lg text-sm font-medium cursor-pointer flex items-center gap-2 transition-colors">
            <Sparkles size={16} />
            Analizar documento
            <input
              type="file"
              accept=".pdf,.txt,.doc,.docx"
              className="hidden"
              onChange={(e) => {
                if (e.target.files?.[0]) handleAnalizar(e.target.files[0]);
                e.target.value = "";
              }}
            />
          </label>
          <button
            onClick={() => { reset({ estado: "Activo" }); setEditingId(null); setModalOpen(true); }}
            className="bg-emerald-700 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium"
          >
            + Nuevo Contrato
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
              <th className="text-left p-3 font-medium">Nº Contrato</th>
              <th className="text-left p-3 font-medium">Cliente ID</th>
              <th className="text-left p-3 font-medium">Inicio</th>
              <th className="text-left p-3 font-medium">Vencimiento</th>
              <th className="text-left p-3 font-medium">Estado</th>
              <th className="text-left p-3 font-medium">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {contratos.map((c: any) => (
              <tr key={c.id} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                <td className="p-3 font-medium text-gray-900 dark:text-white">
                  {c.numero_contrato}
                  {esProximo(c.fecha_vencimiento) && <AlertTriangle size={14} className="inline ml-1 text-amber-500" />}
                </td>
                <td className="p-3 text-gray-700 dark:text-gray-300">{c.cliente_id}</td>
                <td className="p-3 text-gray-700 dark:text-gray-300">{c.fecha_inicio}</td>
                <td className="p-3 text-gray-700 dark:text-gray-300">{c.fecha_vencimiento}</td>
                <td className="p-3">
                  <span className="bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400 px-2 py-0.5 rounded text-xs">
                    {c.estado}
                  </span>
                </td>
                <td className="p-3">
                  <button
                    onClick={() => {
                      setEditingId(c.id);
                      setValue("numero_contrato", c.numero_contrato);
                      setValue("cliente_id", c.cliente_id);
                      setValue("fecha_inicio", c.fecha_inicio);
                      setValue("fecha_vencimiento", c.fecha_vencimiento);
                      setValue("estado", c.estado);
                      setModalOpen(true);
                    }}
                    className="text-gray-500 hover:text-emerald-600 mr-2"
                  >
                    <Pencil size={16} />
                  </button>
                  <button onClick={() => deleteContrato(c.id)} className="text-gray-500 hover:text-red-600">
                    <Trash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
            {contratos.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center py-6 text-gray-500 dark:text-gray-400">
                  No hay contratos registrados
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {modalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md shadow-xl"
          >
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">
                {editingId ? "Editar" : "Nuevo"} Contrato
              </h2>
              <button onClick={() => setModalOpen(false)}>
                <X size={20} className="text-gray-500" />
              </button>
            </div>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
              <input {...register("numero_contrato")} placeholder="Número de contrato*" className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white placeholder-gray-400" required />
              <select {...register("cliente_id")} className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white" required>
                <option value="">Selecciona un cliente</option>
                {clientes.map((cli: any) => <option key={cli.id} value={cli.id}>{cli.nombre}</option>)}
              </select>
              <input {...register("fecha_inicio")} type="date" className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white" required />
              <input {...register("fecha_vencimiento")} type="date" className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white" required />
              <select {...register("estado")} className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white">
                <option value="Activo">Activo</option>
                <option value="Vencido">Vencido</option>
                <option value="Cancelado">Cancelado</option>
              </select>
              <button type="submit" disabled={loading} className="w-full bg-emerald-700 hover:bg-emerald-600 text-white py-2 rounded-lg text-sm font-medium disabled:opacity-50">
                {loading ? "Guardando..." : "Guardar"}
              </button>
            </form>
          </motion.div>
        </div>
      )}

      {analisisModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto shadow-xl"
          >
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <Sparkles size={20} className="text-violet-500" />
                Análisis de Documento
              </h2>
              <button onClick={() => setAnalisisModal(false)}>
                <X size={20} className="text-gray-500" />
              </button>
            </div>
            {analizando ? (
              <div className="text-center py-8">
                <div className="animate-spin w-10 h-10 border-4 border-violet-600 border-t-transparent rounded-full mx-auto mb-4"></div>
                <p className="text-gray-500 dark:text-gray-400">Analizando documento con IA...</p>
                <p className="text-xs text-gray-400 mt-1">Esto puede tomar unos segundos</p>
              </div>
            ) : (
              <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-4 whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 max-h-[60vh] overflow-y-auto">
                {analisisResult || "Sin resultado"}
              </div>
            )}
          </motion.div>
        </div>
      )}
    </div>
  );
}
