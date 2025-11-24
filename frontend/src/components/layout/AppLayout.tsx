import { Outlet } from "react-router-dom";

export default function AppLayout() {
  return (
    <div className="flex h-screen w-full bg-background">
      {/* Sidebar Placeholder */}
      <aside className="w-64 border-r bg-muted/40 hidden md:block">
        <div className="p-4 font-bold">TFG Chatbot</div>
        <nav className="p-4 space-y-2">
          <div className="text-sm">Sidebar Navigation</div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <header className="h-14 border-b flex items-center px-4">
          <div className="font-semibold">Header</div>
        </header>
        <Outlet />
      </main>
    </div>
  );
}
