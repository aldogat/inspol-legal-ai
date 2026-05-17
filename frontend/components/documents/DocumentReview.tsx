"use client"
import { useState } from "react"
import { motion } from "framer-motion"

export function DocumentReview({ analysis }: { analysis: any }) {
  const [selectedClause, setSelectedClause] = useState<any>(null)

  const trafficColor = analysis?.traffic_light === "green" ? "bg-green-500" :
                       analysis?.traffic_light === "yellow" ? "bg-yellow-500" : "bg-red-500"

  if (!analysis) return <div className="p-6">Cargando análisis...</div>

  return (
    <div className="grid grid-cols-3 gap-6 h-full p-6">
      <div className="col-span-2 bg-white dark:bg-gray-800 rounded-xl p-6 border">
        <h2 className="text-lg font-semibold mb-4">Contrato</h2>
        <p className="text-gray-500">Vista previa del documento</p>
      </div>
      <div className="space-y-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border text-center">
          <div className={`w-4 h-4 rounded-full mx-auto mb-2 ${trafficColor}`} />
          <div className="text-3xl font-bold">{analysis.risk_score}/100</div>
          <div className="text-sm text-gray-500">Score de riesgo</div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border">
          <h3 className="font-semibold mb-2">Resumen</h3>
          <p className="text-sm">{analysis.summary}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border">
          <h3 className="font-semibold mb-2">Riesgos</h3>
          {analysis.risks?.map((risk: any, i: number) => (
            <button key={i} onClick={() => setSelectedClause(risk)}
              className="w-full text-left p-2 rounded text-sm bg-red-50 dark:bg-red-900/20 mb-1">
              {risk.clause?.substring(0, 50)}...
            </button>
          ))}
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border">
          <h3 className="font-semibold mb-2">Cláusulas faltantes</h3>
          <ul className="text-sm space-y-1">
            {analysis.missing_clauses?.map((c: string, i: number) => (
              <li key={i}>+ {c}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
