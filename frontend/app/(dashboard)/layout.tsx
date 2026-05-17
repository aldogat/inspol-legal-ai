"use client"
import { useState, useEffect } from "react"
import Link from "next/link"
import { Home, MessageCircle, Scale, Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"

function ThemeToggle() {
  const [mounted, setMounted] = useState(false)
  const { theme, setTheme } = useTheme()

  useEffect(() => setMounted(true), [])

  if (!mounted) return <div className="w-5 h-5" />

  return (
    <button
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
    >
      {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
    </button>
  )
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <aside className="w-64 bg-white dark:bg-gray-800 border-r p-4 flex flex-col gap-4">
        <Link href="/" className="flex items-center gap-2 text-primary">
          <Scale size={28} />
          <span className="font-bold text-xl">INSPOL</span>
        </Link>
        <nav className="flex flex-col gap-2">
          <Link href="/" className="flex items-center gap-2 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
            <Home size={18} /> Dashboard
          </Link>
          <Link href="/chat" className="flex items-center gap-2 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
            <MessageCircle size={18} /> Chat IA
          </Link>
        </nav>
        <div className="mt-auto">
          <ThemeToggle />
        </div>
      </aside>
      <main className="flex-1 p-6 overflow-auto">{children}</main>
    </div>
  )
}
