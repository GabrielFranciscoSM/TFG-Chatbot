import { useAuth } from "@/context/AuthContext";

export default function ChatPage() {
  const { user } = useAuth();

  return (
    <div className="flex flex-col h-full">
      {/* Chat Header */}
      <div className="p-4 border-b">
        <h1 className="text-xl font-semibold">Chat</h1>
        <p className="text-sm text-muted-foreground">
          Bienvenido, {user?.email}
        </p>
      </div>

      {/* Messages Area - Placeholder */}
      <div className="flex-1 overflow-auto p-4">
        <div className="flex items-center justify-center h-full text-muted-foreground">
          <p>Los mensajes aparecerán aquí</p>
        </div>
      </div>

      {/* Input Area - Placeholder */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Escribe tu mensaje..."
            className="flex-1 px-4 py-2 border rounded-md bg-background"
            disabled
          />
          <button
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md opacity-50 cursor-not-allowed"
            disabled
          >
            Enviar
          </button>
        </div>
        <p className="text-xs text-muted-foreground mt-2 text-center">
          La funcionalidad de chat se implementará en la Semana 2
        </p>
      </div>
    </div>
  );
}
