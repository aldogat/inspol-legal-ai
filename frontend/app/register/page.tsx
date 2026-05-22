"use client";
import { useState } from "react";
import { useAuth } from "@/app/context/AuthContext";
import Link from "next/link";

export default function RegisterPage() {
  const { register } = useAuth();
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await register(email, password, nombre);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#050816]">
      <div className="bg-white/5 border border-white/10 rounded-3xl p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6 text-white">Registrarse</h1>
        {error && <p className="text-red-400 mb-4">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Nombre (opcional)"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            className="w-full bg-white/10 border border-white/10 rounded-lg p-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-white/10 border border-white/10 rounded-lg p-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
            required
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-white/10 border border-white/10 rounded-lg p-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
            required
          />
          <button type="submit" className="w-full bg-blue-600 py-3 rounded-xl hover:bg-blue-500 text-white font-semibold">
            Registrarse
          </button>
        </form>
        <p className="mt-4 text-center text-gray-400">
          ¿Ya tienes cuenta? <Link href="/login" className="text-blue-400">Inicia sesión</Link>
        </p>
      </div>
    </div>
  );
}
