"use client";
import { useState, useRef } from "react";
import { Send, Paperclip, Loader, FileText, X } from "lucide-react";

export default function ChatPage() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "👋 Hola, soy tu copiloto jurídico. Puedes preguntarme o adjuntar un documento/audio para que lo analice." }
  ]);
  const [input, setInput] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = async () => {
    if (!input.trim() && !file) return;
    setLoading(true);
    const newMessages = [...messages, { role: "user", content: input || `[Archivo: ${file?.name}]` }];
    setMessages(newMessages);
    setInput("");
    const currentFile = file;
    setFile(null);

    try {
      let response;
      if (currentFile) {
        const formData = new FormData();
        formData.append("file", currentFile);
        if (input.trim()) formData.append("consulta", input);
        response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chat/multimodal`, {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chat/multimodal`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ consulta: input }),
        });
      }

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      const assistantMsg = { role: "assistant", content: data.respuesta };
      setMessages([...newMessages, assistantMsg]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages([...newMessages, { role: "assistant", content: "Error al procesar la solicitud." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files?.[0]) setFile(e.dataTransfer.files[0]);
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4" onDragOver={(e) => e.preventDefault()} onDrop={handleDrop}>
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-md p-3 rounded-lg ${msg.role === "user" ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-800"}`}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-center">
            <Loader className="animate-spin text-gray-500" />
          </div>
        )}
      </div>
      {file && (
        <div className="flex items-center gap-2 p-2 bg-gray-100 rounded-md mb-2">
          <FileText />
          <span className="text-sm truncate">{file.name}</span>
          <button onClick={() => setFile(null)} className="ml-auto text-red-500">
            <X />
          </button>
        </div>
      )}
      <div className="flex gap-2">
        <button onClick={() => fileInputRef.current?.click()} className="p-2 bg-gray-200 rounded-full cursor-pointer">
          <Paperclip />
        </button>
        <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" />
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSend()}
          placeholder="Escribe tu consulta jurídica..."
          className="flex-1 p-2 border rounded-md"
        />
        <button onClick={handleSend} disabled={loading} className="p-2 bg-blue-500 text-white rounded-full">
          <Send />
        </button>
      </div>
    </div>
  );
}
