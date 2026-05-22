"use client";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { motion } from "framer-motion";
import { Pencil, Trash2, X } from "lucide-react";
import { apiFetch } from "@/app/lib/api";
import toast from "react-hot-toast";

const API = "http://localhost:8000/api/v1";

export default function ClientesPage() {
  const [clientes, setClientes] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit, reset, setValue } = useForm();

  useEffect(() => { fetchClientes(); }, []);

  const fetchClientes = async () => {
    try {
      const r = await apiFetch(`${API}/clientes/`);
      if (!r.ok) throw new Error("Error al cargar");
      setClientes(await r.json());
    } catch (e: any) { toast.error(e.message); }
  };

  const onSubmit = async (fd: any) => {
    setLoading(true);
    try {
      const url = editingId ? `${API}/clientes/${editingId}` : `${API}/clientes/`;
      const res = await apiFetch(url, { method: editingId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(fd) });
      if (!res.ok) throw new Error((await res.json()).detail || "Error");
      toast.success(editingId ? "Cliente actualizado" : "Cliente creado");
      fetchClientes(); setModalOpen(false);
    } catch (e: any) { toast.error(e.message); }
    finally { setLoading(false); }
  };

  const deleteCliente = async (id: number) => {
    if (!confirm("¿Eliminar?")) return;
    try { await apiFetch(`${API}/clientes/${id}`, { method: "DELETE" }); toast.success("Eliminado"); fetchClientes(); }
    catch (e: any) { toast.error(e.message); }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Clientes</h1>
        <button onClick={() => { reset({}); setEditingId(null); setModalOpen(true); }} className="bg-gray-900 dark:bg-white text-white dark:text-gray-900 px-4 py-2 rounded-lg text-sm font-medium">+ Nuevo</button>
      </div>

      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead><tr className="text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700"><th className="text-left p-3 font-medium">Nombre</th><th className="text-left p-3 font-medium">Email</th><th className="text-left p-3 font-medium">Teléfono</th><th className="text-left p-3 font-medium">RFC</th><th className="text-left p-3 font-medium">Acciones</th></tr></thead>
          <tbody>
            {clientes.map((c: any) => (
              <tr key={c.id} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                <td className="p-3 font-medium text-gray-900 dark:text-white">{c.nombre}</td>
                <td className="p-3 text-gray-700 dark:text-gray-300">{c.email}</td>
                <td className="p-3 text-gray-700 dark:text-gray-300">{c.telefono || "-"}</td>
                <td className="p-3 text-gray-700 dark:text-gray-300">{c.rfc || "-"}</td>
                <td className="p-3">
                  <button onClick={() => { setEditingId(c.id); setValue("nombre", c.nombre); setValue("email", c.email); setValue("telefono", c.telefono||""); setValue("rfc", c.rfc||""); setValue("direccion", c.direccion||""); setModalOpen(true); }} className="text-gray-500 hover:text-blue-600 mr-2"><Pencil size={16} /></button>
                  <button onClick={() => deleteCliente(c.id)} className="text-gray-500 hover:text-red-600"><Trash2 size={16} /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md shadow-xl">
            <div className="flex justify-between items-center mb-4"><h2 className="text-lg font-bold text-gray-900 dark:text-white">{editingId?"Editar":"Nuevo"}</h2><button onClick={() => setModalOpen(false)}><X size={20} className="text-gray-500" /></button></div>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
              <input {...register("nombre")} placeholder="Nombre*" className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white placeholder-gray-400" required />
              <input {...register("email")} type="email" placeholder="Email*" className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white placeholder-gray-400" required />
              <input {...register("telefono")} placeholder="Teléfono" className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white placeholder-gray-400" />
              <input {...register("rfc")} placeholder="RFC" className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white placeholder-gray-400" />
              <textarea {...register("direccion")} placeholder="Dirección" rows={2} className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-lg p-2 text-sm text-gray-900 dark:text-white placeholder-gray-400" />
              <button type="submit" disabled={loading} className="w-full bg-gray-900 dark:bg-white text-white dark:text-gray-900 py-2 rounded-lg text-sm font-medium">{loading?"Guardando...":"Guardar"}</button>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
}
