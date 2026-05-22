"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Briefcase,
  Users,
  FileText,
  CalendarDays,
  BarChart3,
  Wallet,
  MessageSquare,
  Sun,
  Moon,
} from "lucide-react";
import { useTheme } from "@/app/context/ThemeContext";

const sidebarItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard" },
  { icon: Briefcase, label: "Expedientes", path: "/dashboard/expedientes" },
  { icon: Users, label: "Clientes", path: "/dashboard/clientes" },
  { icon: FileText, label: "Contratos", path: "/dashboard/contratos" },
  { icon: CalendarDays, label: "Calendario", path: "/dashboard/calendario" },
  { icon: Wallet, label: "Finanzas", path: "/dashboard/finanzas" },
  { icon: BarChart3, label: "Reportes", path: "/dashboard/reportes" },
  { icon: MessageSquare, label: "Chat IA", path: "/dashboard/chat" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 flex transition-colors">
      <aside className="w-[240px] bg-gray-900 dark:bg-gray-950 border-r border-gray-800 flex flex-col justify-between">
        <div className="p-5">
          <div className="flex items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center">
              <span className="text-gray-900 font-bold text-sm">I</span>
            </div>
            <div>
              <h1 className="text-base font-semibold text-white">INSPOL</h1>
              <p className="text-[10px] text-amber-500 uppercase tracking-widest">Legal</p>
            </div>
          </div>
          <nav className="space-y-0.5">
            {sidebarItems.map((item) => (
              <Link key={item.path} href={item.path}>
                <div className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  pathname === item.path
                    ? "bg-gray-800 text-white border-l-2 border-amber-500"
                    : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
                }`}>
                  <item.icon size={16} />
                  <span>{item.label}</span>
                </div>
              </Link>
            ))}
          </nav>
        </div>
        <div className="p-4 border-t border-gray-800">
          <button onClick={toggleTheme} className="flex items-center gap-2 text-sm text-gray-400 hover:text-white w-full px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors">
            {theme === "light" ? <Moon size={16} /> : <Sun size={16} />}
            <span>{theme === "light" ? "Modo Oscuro" : "Modo Claro"}</span>
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto bg-gray-50 dark:bg-gray-900 transition-colors">
        {children}
      </main>
    </div>
  );
}
