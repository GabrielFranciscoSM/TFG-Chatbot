import { Plus } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { ChatInput } from "@/components/chat/ChatInput";
import { MessageList } from "@/components/chat/MessageList";
import { NewSessionDialog } from "@/components/chat/NewSessionDialog";
import { SessionSelector } from "@/components/chat/SessionSelector";
import { Button } from "@/components/ui/button";
import { useChat } from "@/hooks/useChat";
import { useSessions } from "@/hooks/useSessions";
import type { ChatSession } from "@/types/chat";

export default function ChatPage() {
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const [showNewSessionDialog, setShowNewSessionDialog] = useState(false);

  const { sessions, isLoading: sessionsLoading, createSession, deleteSession } = useSessions();

  const {
    messages,
    isLoading: chatLoading,
    isInterrupted,
    sendMessage,
    resumeTest,
  } = useChat({
    sessionId: activeSession?.id || null,
    subject: activeSession?.subject,
  });

  const handleSelectSession = (session: ChatSession) => {
    setActiveSession(session);
  };

  const handleNewSession = () => {
    setShowNewSessionDialog(true);
  };

  const handleCreateSession = async (title: string, subject: string) => {
    const session = await createSession(title, subject);
    if (session) {
      setActiveSession(session);
      toast.success("Conversación creada");
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    const success = await deleteSession(sessionId);
    if (success) {
      if (activeSession?.id === sessionId) {
        setActiveSession(null);
      }
      toast.success("Conversación eliminada");
    }
  };

  const handleSendMessage = async (content: string) => {
    if (isInterrupted) {
      await resumeTest(content);
    } else {
      await sendMessage(content);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Chat Header with Session Selector */}
      <div className="flex items-center gap-3 p-3 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <SessionSelector
          sessions={sessions}
          activeSession={activeSession}
          isLoading={sessionsLoading}
          onSelectSession={handleSelectSession}
          onNewSession={handleNewSession}
          onDeleteSession={handleDeleteSession}
        />
        {activeSession && (
          <span className="text-sm text-muted-foreground">{activeSession.subject}</span>
        )}
      </div>

      {/* Messages Area */}
      {activeSession ? (
        <>
          <MessageList messages={messages} isLoading={chatLoading} />
          <ChatInput
            onSend={handleSendMessage}
            isLoading={chatLoading}
            placeholder={isInterrupted ? "Escribe tu respuesta..." : "Escribe tu mensaje..."}
          />
        </>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-4">
            <div className="text-6xl">💬</div>
            <h2 className="text-xl font-semibold">Bienvenido al Chat</h2>
            <p className="text-muted-foreground max-w-md">
              Crea una nueva conversación para empezar a chatear con el asistente educativo
            </p>
            <Button onClick={handleNewSession} size="lg" className="gap-2">
              <Plus className="h-5 w-5" />
              Nueva conversación
            </Button>
          </div>
        </div>
      )}

      {/* New Session Dialog */}
      <NewSessionDialog
        open={showNewSessionDialog}
        onOpenChange={setShowNewSessionDialog}
        onCreateSession={handleCreateSession}
      />
    </div>
  );
}
