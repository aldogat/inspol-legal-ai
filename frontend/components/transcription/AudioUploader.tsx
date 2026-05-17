"use client"
import { useState } from "react"
import { Mic, Loader } from "lucide-react"

export function AudioUploader() {
  const [file, setFile] = useState<File|null>(null)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const upload = async () => {
    if (!file) return
    setLoading(true)
    const fd = new FormData()
    fd.append("file", file)
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/transcription/transcribe`, { method:"POST", body: fd })
    const data = await res.json()
    setResult(data.transcription)
    setLoading(false)
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 space-y-4">
      <h2 className="text-lg font-semibold">Transcripción de audio</h2>
      <input type="file" accept="audio/*" onChange={e=>setFile(e.target.files?.[0]||null)} className="hidden" id="audio" />
      <label htmlFor="audio" className="block border-2 border-dashed p-8 rounded-xl text-center cursor-pointer">
        <Mic size={32} className="mx-auto text-gray-400" />
        <p className="text-sm mt-2">{file ? file.name : "Seleccionar audio"}</p>
      </label>
      {file && <button onClick={upload} disabled={loading} className="w-full py-2 bg-primary text-white rounded-lg">
        {loading ? <Loader className="animate-spin mx-auto" size={16}/> : "Transcribir"}
      </button>}
      {result && (
        <div className="space-y-2">
          <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded">
            <p className="font-medium text-sm">Resumen</p>
            <p className="text-sm">{result.summary}</p>
          </div>
          <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded">
            <p className="font-medium text-sm">Transcripción</p>
            <p className="text-sm whitespace-pre-wrap">{result.text}</p>
          </div>
        </div>
      )}
    </div>
  )
}
