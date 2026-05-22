"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Scale, Briefcase, Users, FileText, CalendarDays, ShieldCheck, Wallet, Plus, AlertCircle, Search } from "lucide-react";
import { LineChart, Line, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, XAxis, Tooltip } from "recharts";
import moment from "moment";
import "moment/locale/es";
import { apiFetch } from "@/app/lib/api";

const API = "http://localhost:8000/api/v1";

const CHART_COLORS = ["#059669", "#b45309", "#7c3aed", "#dc2626"];
const LINE_COLOR = "#059669";
const BAR_COLOR = "#7c3aed";

export default function DashboardPage() {
  const router = useRouter();
  const [estadisticas, setEstadisticas] = useState<any>(null);
  const [pregunta, setPregunta] = useState("");
  const [respuestaIa, setRespuestaIa] = useState("");
  const [cargandoIA, setCargandoIA] = useState(false);

  const fetchEstadisticas = async () => {
    try {
      const res = await apiFetch(`${API}/estadisticas/`);
      if (!res.ok) throw new Error("Error");
      setEstadisticas(await res.json());
    } catch (err) { console.error(err); }
  };

  useEffect(() => {
    fetchEstadisticas();
    const interval = setInterval(fetchEstadisticas, 30000);
    const h = () => { if (document.visibilityState === "visible") fetchEstadisticas(); };
    document.addEventListener("visibilitychange", h);
    return () => { clearInterval(interval); document.removeEventListener("visibilitychange", h); };
  }, []);

  const enviarPregunta = async (texto: string) => {
    setCargandoIA(true); setRespuestaIa("");
    try {
      const res = await apiFetch(`${API}/chat/multimodal`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ consulta: texto }) });
      if (!res.ok) throw new Error("Error");
      setRespuestaIa((await res.json()).respuesta);
    } catch (err: any) { setRespuestaIa("Error: " + err.message); }
    finally { setCargandoIA(false); }
  };

  const formatMonto = (m: number) => `$${m.toLocaleString("es-MX")}`;

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Buenos días, Licenciado 👋</h2>
          <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Resumen ejecutivo del despacho</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-2.5 flex items-center gap-2 w-[300px]">
            <Search size={16} className="text-gray-400" />
            <input className="bg-transparent outline-none w-full text-sm text-gray-900 dark:text-white placeholder-gray-400" placeholder="Buscar..." />
          </div>
          <Link href="/dashboard/expedientes" className="bg-emerald-700 hover:bg-emerald-600 text-white px-4 py-2.5 rounded-xl text-sm font-medium flex items-center gap-2 transition-colors">
            <Plus size={16} /> Nuevo Caso
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { icon: Wallet, color: "emerald", title: `${estadisticas?.total_transacciones || 0} transacciones`, sub: "Finanzas registradas" },
          { icon: AlertCircle, color: "amber", title: `${estadisticas?.contratos_por_vencer || 0} contratos por vencer`, sub: "Próximos 30 días" },
          { icon: Briefcase, color: "red", title: `${estadisticas?.casos_activos || 0} casos activos`, sub: "Requieren seguimiento" },
        ].map((a, i) => (
          <div key={i} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4 flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
              a.color === "emerald" ? "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400" :
              a.color === "amber" ? "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400" :
              "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400"
            }`}>
              <a.icon size={18} />
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">{a.title}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{a.sub}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-5 gap-4 mb-6">
        {[
          { t: "Casos Activos", v: estadisticas?.casos_activos || 0, i: Briefcase },
          { t: "Casos Cerrados", v: estadisticas?.casos_cerrados || 0, i: ShieldCheck },
          { t: "Total Clientes", v: estadisticas?.total_clientes || 0, i: Users },
          { t: "Contratos", v: estadisticas?.total_contratos || 0, i: FileText },
          { t: "Balance", v: formatMonto(estadisticas?.balance || 0), i: Wallet },
        ].map((k, i) => (
          <div key={i} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3"><k.i size={18} className="text-gray-700 dark:text-gray-300" /><p className="text-xs text-gray-500 dark:text-gray-400">{k.t}</p></div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{k.v}</h3>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="col-span-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-emerald-700 flex items-center justify-center"><Scale size={18} className="text-white" /></div>
            <div><h3 className="text-base font-bold text-gray-900 dark:text-white">INSPOL LEGAL AI</h3><p className="text-xs text-gray-500 dark:text-gray-400">Inteligencia Jurídica Mexicana</p></div>
          </div>
          <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-3 mb-4 flex items-center gap-2">
            <input className="bg-transparent outline-none w-full text-sm text-gray-900 dark:text-white placeholder-gray-400" placeholder="Pregúntale algo a la IA..." value={pregunta} onChange={(e) => setPregunta(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && (pregunta.trim() && (enviarPregunta(pregunta), setPregunta("")))} />
            <button onClick={() => { enviarPregunta(pregunta); setPregunta(""); }} disabled={cargandoIA} className="bg-emerald-700 hover:bg-emerald-600 text-white px-4 py-1.5 rounded-lg text-sm disabled:opacity-50">{cargandoIA ? '...' : 'Enviar'}</button>
          </div>
          {respuestaIa && <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-4 mb-4 text-sm text-gray-700 dark:text-gray-300 max-h-[200px] overflow-y-auto whitespace-pre-wrap">{respuestaIa}</div>}
          <div className="grid grid-cols-4 gap-2">
            {[
              { t: "Generar Demanda", a: () => enviarPregunta("Genera un borrador de demanda civil mexicana.") },
              { t: "Analizar Contrato", a: () => router.push("/dashboard/contratos") },
              { t: "Resumen Expediente", a: () => router.push("/dashboard/expedientes") },
              { t: "Investigación Legal", a: () => enviarPregunta("Investigación sobre elementos esenciales de contratos en derecho mexicano.") },
            ].map((b, i) => (
              <button key={i} onClick={b.a} disabled={cargandoIA} className="bg-gray-50 dark:bg-gray-900 hover:bg-gray-100 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700 rounded-xl p-3 text-sm text-gray-700 dark:text-gray-300 transition-colors text-left">{b.t}</button>
            ))}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-4">ALERTAS LEGALES</h3>
          <div className="space-y-3">
            {estadisticas?.contratos_por_vencer > 0 && <AlertItem t={`${estadisticas.contratos_por_vencer} contrato(s) por vencer`} type="Urgente" />}
            {estadisticas?.casos_activos > 0 && <AlertItem t={`${estadisticas.casos_activos} expediente(s) activo(s)`} type="Importante" />}
            {estadisticas?.eventos_proximos?.length > 0 && <AlertItem t={`${estadisticas.eventos_proximos.length} evento(s) próximo(s)`} type="Pendiente" />}
            <div className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-3">
              <p className="text-sm text-gray-700 dark:text-gray-300">Balance: <span className="font-bold">{formatMonto(estadisticas?.balance || 0)}</span></p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Productividad Semanal</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={estadisticas?.productividad_semanal || []}>
              <Line type="monotone" dataKey="value" stroke={LINE_COLOR} strokeWidth={3} dot={{ fill: LINE_COLOR, r: 4 }} />
              <Tooltip />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Casos por Prioridad</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={estadisticas?.casos_por_area || []} dataKey="value" outerRadius={70} innerRadius={40}>
                {(estadisticas?.casos_por_area || []).map((_: any, i: number) => (
                  <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-4 mt-2">
            {(estadisticas?.casos_por_area || []).map((item: any, i: number) => (
              <div key={i} className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                <div className="w-2 h-2 rounded-full" style={{ background: CHART_COLORS[i % CHART_COLORS.length] }}></div>
                {item.name}
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Ingresos Mensuales</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={estadisticas?.ahorro_ia || []}>
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" fill={BAR_COLOR} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase">Expedientes Activos</h3>
          <Link href="/dashboard/expedientes" className="text-xs text-emerald-700 dark:text-emerald-400 hover:underline">Ver todos</Link>
        </div>
        <table className="w-full text-sm">
          <thead><tr className="text-gray-400 border-b border-gray-200 dark:border-gray-700"><th className="text-left py-2 font-medium">Expediente</th><th className="text-left py-2 font-medium">Cliente</th><th className="text-left py-2 font-medium">Estado</th><th className="text-left py-2 font-medium">Prioridad</th><th className="text-left py-2 font-medium">Fecha</th></tr></thead>
          <tbody>
            {estadisticas?.expedientes_activos?.length > 0 ? estadisticas.expedientes_activos.map((exp: any) => (
              <tr key={exp.id} className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                <td className="py-2 font-medium text-gray-900 dark:text-white">{exp.numero_expediente}</td>
                <td className="py-2 text-gray-700 dark:text-gray-300">{exp.cliente}</td>
                <td className="py-2"><span className="bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-400 px-2 py-0.5 rounded text-xs">{exp.estado}</span></td>
                <td className="py-2"><span className={`px-2 py-0.5 rounded text-xs ${exp.prioridad==="Alta"?"bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-400":"bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-400"}`}>{exp.prioridad}</span></td>
                <td className="py-2 text-xs text-gray-500 dark:text-gray-400">{exp.fecha_apertura ? moment(exp.fecha_apertura).format("DD MMM YYYY") : "-"}</td>
              </tr>
            )) : <tr><td colSpan={5} className="text-center py-6 text-gray-500 dark:text-gray-400">No hay expedientes activos</td></tr>}
          </tbody>
        </table>
      </div>

      {estadisticas?.eventos_proximos?.length > 0 && (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase">Próximos Eventos</h3>
            <Link href="/dashboard/calendario" className="text-xs text-emerald-700 dark:text-emerald-400 hover:underline">Ver calendario</Link>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {estadisticas.eventos_proximos.map((ev: any) => (
              <div key={ev.id} className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-3 flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-700 text-white flex items-center justify-center text-sm font-bold">{moment(ev.fecha_inicio).format("D")}</div>
                <div><p className="text-sm font-medium text-gray-900 dark:text-white">{ev.titulo}</p><p className="text-xs text-gray-500 dark:text-gray-400">{moment(ev.fecha_inicio).format("D MMM, h:mm A")}</p></div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function AlertItem({ t, type }: { t: string; type: string }) {
  const colors: any = {
    Urgente: "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-700 dark:text-red-400",
    Importante: "bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-400",
    Pendiente: "bg-violet-50 dark:bg-violet-900/20 border-violet-200 dark:border-violet-800 text-violet-700 dark:text-violet-400"
  };
  return <div className={`rounded-xl p-3 border ${colors[type]}`}><p className="text-sm">{t}<span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-white/50 dark:bg-black/20">{type}</span></p></div>;
}
