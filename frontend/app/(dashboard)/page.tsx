export default function Dashboard() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Buenos días, Carlos</h1>
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow"><p className="text-gray-500">Casos activos</p><p className="text-3xl font-bold">24</p></div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow"><p className="text-gray-500">Documentos</p><p className="text-3xl font-bold">12</p></div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow"><p className="text-gray-500">Vencimientos</p><p className="text-3xl font-bold">3</p></div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow"><p className="text-gray-500">Horas ahorradas</p><p className="text-3xl font-bold">89</p></div>
      </div>
    </div>
  )
}
