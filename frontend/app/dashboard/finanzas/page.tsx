"use client";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { motion } from "framer-motion";
import { Pencil, Trash2, X, Plus, TrendingUp, TrendingDown, DollarSign } from "lucide-react";
import { apiFetch } from "@/app/lib/api";

const API = "http://localhost:8000/api/v1";

export default function FinanzasPage() {
  const [transacciones, setTransacciones] = useState([]);
  const [resumen, setResumen] = useState({ total_ingresos: 0, total_gastos: 0, balance: 0, total_transacciones: 0 });
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("");

  const { register, handleSubmit, reset, setValue } = useForm();

  useEffect(() => {
    fetchTransacciones();
    fetchResumen();
  }, []);

  const fetchTransacciones = async (tipo = "") => {
    try {
      const url = tipo ? `${API}/finanzas/?tipo=${encodeURIComponent(tipo)}` : `${API}/finanzas/`;
      const res = await apiFetch(url);
      if (!res.ok) throw new Error("Error al cargar transacciones");
      const data = await res.json();
      setTransacciones(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message);
    }
  };

  const fetchResumen = async () => {
    try {
      const res = await apiFetch(`${API}/finanzas/resumen`);
      if (!res.ok) throw new Error("Error al cargar resumen");
      const data = await res.json();
      setResumen(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const openNewModal = () => {
    reset({ tipo: "Ingreso", categoria: "Honorarios", monto: 0, fecha: new Date().toISOString().slice(0, 16), descripcion: "" });
    setEditingId(null);
    setModalOpen(true);
  };

  const openEditModal = (trans) => {
    setEditingId(trans.id);
    setValue("tipo", trans.tipo);
    setValue("categoria", trans.categoria);
    setValue("monto", trans.monto);
    setValue("fecha", trans.fecha.slice(0, 16));
    setValue("descripcion", trans.descripcion || "");
    setModalOpen(true);
  };

  const closeModal = () => setModalOpen(false);

  const onSubmit = async (formData) => {
    setLoading(true);
    setError("");
    try {
      const payload = { ...formData, monto: parseFloat(formData.monto), fecha: new Date(formData.fecha).toISOString() };
      const url = editingId ? `${API}/finanzas/${editingId}` : `${API}/finanzas/`;
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
      await fetchTransacciones(filtroTipo);
      await fetchResumen();
      closeModal();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteTransaccion = async (id) => {
    if (!confirm("¿Eliminar transacción?")) return;
    try {
      await apiFetch(`${API}/finanzas/${id}`, { method: "DELETE" });
      setTransacciones(transacciones.filter((t) => t.id !== id));
      fetchResumen();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleFiltro = (tipo) => {
    setFiltroTipo(tipo);
    fetchTransacciones(tipo);
  };

  const formatMonto = (monto) => `$${monto.toLocaleString("es-MX", { minimumFractionDigits: 2 })}`;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Finanzas</h1>
        <button onClick={openNewModal} className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg flex items-center gap-2">
          <Plus size={18} /> Nueva Transacción
        </button>
      </div>
      {error && <p className="text-red-400 mb-4">{error}</p>}
      <div className="grid grid-cols-4 gap-5 mb-8">
        <ResumenCard title="Ingresos Totales" value={formatMonto(resumen.total_ingresos)} icon={TrendingUp} color="from-green-500 to-emerald-500" />
        <ResumenCard title="Gastos Totales" value={formatMonto(resumen.total_gastos)} icon={TrendingDown} color="from-red-500 to-pink-500" />
        <ResumenCard title="Balance" value={formatMonto(resumen.balance)} icon={DollarSign} color={resumen.balance >= 0 ? "from-blue-500 to-cyan-500" : "from-orange-500 to-red-500"} />
        <ResumenCard title="Transacciones" value={resumen.total_transacciones.toString()} icon={DollarSign} color="from-purple-500 to-indigo-500" />
      </div>
      <div className="flex gap-3 mb-6">
        <button onClick={() => handleFiltro("")} className={`px-4 py-2 rounded-lg ${filtroTipo === "" ? "bg-blue-600" : "bg-white/10 hover:bg-white/20"}`}>Todas</button>
        <button onClick={() => handleFiltro("Ingreso")} className={`px-4 py-2 rounded-lg ${filtroTipo === "Ingreso" ? "bg-blue-600" : "bg-white/10 hover:bg-white/20"}`}>Ingresos</button>
        <button onClick={() => handleFiltro("Gasto")} className={`px-4 py-2 rounded-lg ${filtroTipo === "Gasto" ? "bg-blue-600" : "bg-white/10 hover:bg-white/20"}`}>Gastos</button>
      </div>
      <div className="bg-white/5 border border-white/10 rounded-3xl p-6 overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="text-gray-400 border-b border-white/10">
              <th className="p-4">Tipo</th><th>Categoría</th><th>Monto</th><th>Fecha</th><th>Descripción</th><th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {transacciones.map((trans) => (
              <tr key={trans.id} className="border-b border-white/5 hover:bg-white/5">
                <td className="p-4"><span className={`px-2 py-1 rounded-full text-xs ${trans.tipo === "Ingreso" ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"}`}>{trans.tipo}</span></td>
                <td>{trans.categoria}</td>
                <td className={trans.tipo === "Ingreso" ? "text-green-400" : "text-red-400"}>{formatMonto(trans.monto)}</td>
                <td>{new Date(trans.fecha).toLocaleDateString("es-MX")}</td>
                <td className="max-w-[200px] truncate">{trans.descripcion || "-"}</td>
                <td>
                  <button onClick={() => openEditModal(trans)} className="p-1 hover:text-blue-400"><Pencil size={18} /></button>
                  <button onClick={() => deleteTransaccion(trans.id)} className="p-1 hover:text-red-400 ml-2"><Trash2 size={18} /></button>
                </td>
              </tr>
            ))}
            {transacciones.length === 0 && (
              <tr><td colSpan={6} className="text-center py-8 text-gray-500">No hay transacciones registradas</td></tr>
            )}
          </tbody>
        </table>
      </div>
      {modalOpen && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="bg-[#0b1020] border border-white/10 rounded-2xl p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">{editingId ? "Editar" : "Nueva"} Transacción</h2>
              <button onClick={closeModal}><X /></button>
            </div>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <select {...register("tipo")} className="w-full bg-white/10 border border-white/10 rounded-lg p-2 text-white" required>
                <option value="Ingreso">Ingreso</option><option value="Gasto">Gasto</option>
              </select>
              <input {...register("categoria")} placeholder="Categoría" className="w-full bg-white/10 border border-white/10 rounded-lg p-2 text-white" required />
              <input {...register("monto")} type="number" step="0.01" min="0" placeholder="Monto" className="w-full bg-white/10 border border-white/10 rounded-lg p-2 text-white" required />
              <input {...register("fecha")} type="datetime-local" className="w-full bg-white/10 border border-white/10 rounded-lg p-2 text-white" required />
              <textarea {...register("descripcion")} placeholder="Descripción" rows={2} className="w-full bg-white/10 border border-white/10 rounded-lg p-2 text-white" />
              <button type="submit" disabled={loading} className="w-full bg-blue-600 py-2 rounded-xl hover:bg-blue-500 disabled:opacity-50 text-white">
                {loading ? "Guardando..." : "Guardar"}
              </button>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
}

function ResumenCard({ title, value, icon: Icon, color }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-3xl p-5">
      <div className={`w-12 h-12 rounded-2xl bg-gradient-to-r ${color} flex items-center justify-center mb-4`}>
        <Icon size={22} />
      </div>
      <p className="text-gray-400 text-sm">{title}</p>
      <h3 className="text-2xl font-bold mt-2">{value}</h3>
    </div>
  );
}
