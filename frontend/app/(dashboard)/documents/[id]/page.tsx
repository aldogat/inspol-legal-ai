"use client"
import { useState, useEffect } from "react"
import { DocumentReview } from "@/components/documents/DocumentReview"
import { useParams } from "next/navigation"

export default function DocumentPage() {
  const { id } = useParams()
  const [analysis, setAnalysis] = useState<any>(null)

  useEffect(() => {
    setAnalysis({
      risk_score: 78,
      traffic_light: "red",
      summary: "Contrato con cláusulas que requieren atención.",
      risks: [
        { clause: "Renuncia a derechos legales", risk: "Cláusula abusiva", severity: "high", suggestion: "Eliminar y proponer mediación imparcial." },
        { clause: "Sin garantía explícita", risk: "Falta de protección", severity: "medium", suggestion: "Incluir garantía de 90 días." }
      ],
      missing_clauses: ["Confidencialidad", "Protección de datos", "Fianza"]
    })
  }, [id])

  return <DocumentReview analysis={analysis} />
}
