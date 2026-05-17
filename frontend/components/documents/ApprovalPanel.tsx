"use client"
import { useState } from "react"
import { Check, X, AlertTriangle } from "lucide-react"

export function ApprovalPanel({ docId, status, onChange }: { docId: string, status: string, onChange: (s: string) => void }) {
  const [comments, setComments] = useState("")

  const handle = async (action: string) => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/approvals/submit`, {
      method: "POST", headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ document_id: docId, action, comments })
    })
    const data = await res.json()
    if (data.status === "ok") onChange(data.new_status)
  }

  return (
    <div className="space-y-3">
      <span className={`px-2 py-1 rounded-full text-xs ${
        status==="approved" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}`}>
        {status==="draft"?"Borrador":"Aprobado"}
      </span>
      {status !== "approved" && (
        <>
          <textarea value={comments} onChange={e=>setComments(e.target.value)} placeholder="Comentarios..."
            className="w-full p-2 border rounded-lg text-sm" />
          <div className="flex gap-2">
            <button onClick={()=>handle("approve")} className="px-3 py-1 bg-green-600 text-white rounded text-sm"><Check size={14}/> Aprobar</button>
            <button onClick={()=>handle("request_changes")} className="px-3 py-1 bg-yellow-600 text-white rounded text-sm"><AlertTriangle size={14}/> Cambios</button>
            <button onClick={()=>handle("reject")} className="px-3 py-1 bg-red-600 text-white rounded text-sm"><X size={14}/> Rechazar</button>
          </div>
        </>
      )}
    </div>
  )
}
