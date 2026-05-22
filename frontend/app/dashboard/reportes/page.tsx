"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { FileSpreadsheet, FileText, Download } from "lucide-react";
import { apiFetch } from "@/app/lib/api";

const API = "http://localhost:8000/api/v1/reportes";

export default function ReportesPage() {
  const [tipo, setTipo] = useState("expedientes");
  const [formato, setFormato] = useState("excel");
  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleDownload = async () => {
    setLoading(true);
    setError("");
    try {
      let url = `${API}/${formato}?tipo=${tipo}`;
      if (desde) url += `&desde=${desde}`;
      if (hasta) url += `&hasta=${hasta}`;
      const response = await apiFetch(url);
      if (!response.ok) throw new Error(`Error al generar el reporte: ${response.statusText}`);
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = `reporte_${tipo}.${formato === "excel" ? "xlsx" : "pdf"}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">Reportes</h1>
      {error && <p className="text-red-400 mb-4">{error}</p>}
      <div className="bg-white/5 border border-white/10 rounded-3xl p-8 max-w-2xl">
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-white/60 mb-2">Tipo de Reporte</label>
            <select value={tipo} onChange={(e) => setTipo(e.target.value)} className="w-full bg-white/10 border border-white/10 rounded-lg p-3 text-white">
              <option value="expedientes">Expedientes</option>
              <option value="clientes">Clientes</option>
              <option value="contratos">Contratos</option>
              <option value="finanzas">Finanzas</option>
            </select>
          </div>
          <div>
            <label className="block text-white/60 mb-2">Formato</label>
            <div className="flex gap-3">
              <button onClick={() => setFormato("excel")} className={`flex-1 flex items-center justify-center gap-2 p-3 rounded-lg border ${formato === "excel" ? "bg-blue-600 border-blue-500" : "bg-white/10 border-white/10 hover:bg-white/20"}`}>
                <FileSpreadsheet size={20} /> Excel
              </button>
              <button onClick={() => setFormato("pdf")} className={`flex-1 flex items-center justify-center gap-2 p-3 rounded-lg border ${formato === "pdf" ? "bg-blue-600 border-blue-500" : "bg-white/10 border-white/10 hover:bg-white/20"}`}>
                <FileText size={20} /> PDF
              </button>
            </div>
          </div>
        </div>
        {(tipo === "expedientes" || tipo === "contratos" || tipo === "finanzas") && (
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-white/60 mb-2">Fecha Desde</label>
              <input type="date" value={desde} onChange={(e) => setDesde(e.target.value)} className="w-full bg-white/10 border border-white/10 rounded-lg p-3 text-white" />
            </div>
            <div>
              <label className="block text-white/60 mb-2">Fecha Hasta</label>
              <input type="date" value={hasta} onChange={(e) => setHasta(e.target.value)} className="w-full bg-white/10 border border-white/10 rounded-lg p-3 text-white" />
            </div>
          </div>
        )}
        <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={handleDownload} disabled={loading} className="w-full bg-blue-600 hover:bg-blue-500 py-4 rounded-xl flex items-center justify-center gap-3 font-medium text-lg disabled:opacity-50 text-white">
          <Download size={22} />
          {loading ? "Generando..." : "Descargar Reporte"}
        </motion.button>
      </div>
    </div>
  );
}
