"use client"
import { useState, useRef } from "react"
import { Send, Paperclip, Loader, FileText, X } from "lucide-react"

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "👋 Hola, soy tu copiloto jurídico. Puedes preguntarme o adjuntar un documento/audio para que lo analice." }
  ])
  const [input, setInput] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSend = async () => {
    if (!input.trim() && !file) return
    setLoading(true)
    const formData = new FormData()
    if (input.trim()) formData.append("message", input)
    if (file) formData.append("file", file)

    const userMsg = { role: "user", content: input || `[Archivo: ${file?.name}]` }
    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setInput("")
    setFile(null)

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chat/multimodal`, {
        method: "POST",
        body: formData
      })
      const data = await res.json()
      const assistantMsg = { role: "assistant", content: data.response }
      setMessages([...newMessages, assistantMsg])
    } catch (e) {
      setMessages([...newMessages, { role: "assistant", content: "Error al procesar la solicitud." }])
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0])
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    if (e.dataTransfer.files?.[0]) setFile(e.dataTransfer.files[0])
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
      <div className="p-4 border-b bg-gradient-to-r from-primary/5 to-secondary/5">
        <h2 className="font-semibold flex items-center gap-2">
          <FileText className="w-5 h-5 text-primary" /> Chat Jurídico Multimodal
        </h2>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}>
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[80%] p-3 rounded-2xl ${
              msg.role === "user" ? "bg-primary text-white rounded-br-md" : "bg-gray-100 dark:bg-gray-700 rounded-bl-md"
            }`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-2xl flex items-center gap-2">
              <Loader className="animate-spin" size={16} /> Analizando archivo...
            </div>
          </div>
        )}
      </div>
      {file && (
        <div className="px-4 py-2 bg-blue-50 dark:bg-blue-900/20 border-t flex items-center gap-2">
          <FileText size={16} className="text-primary" />
          <span className="text-sm flex-1 truncate">{file.name}</span>
          <button onClick={() => setFile(null)} className="text-gray-500 hover:text-red-500">
            <X size={16} />
          </button>
        </div>
      )}
      <form onSubmit={e => { e.preventDefault(); handleSend() }} className="p-4 border-t flex items-end gap-2">
        <button type="button" onClick={() => fileInputRef.current?.click()} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
          <Paperclip size={20} />
        </button>
        <input ref={fileInputRef} type="file" onChange={handleFileChange} className="hidden"
          accept=".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg,.mp3,.wav,.m4a,.ogg,.webm" />
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Escribe tu consulta o adjunta un archivo..."
          className="flex-1 p-2 border rounded-lg resize-none dark:bg-gray-700 min-h-[40px] max-h-[120px]"
          rows={1}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend() } }}
        />
        <button type="submit" disabled={loading} className="p-2 bg-primary text-white rounded-lg hover:bg-primary/90">
          <Send size={20} />
        </button>
      </form>
    </div>
  )
}
