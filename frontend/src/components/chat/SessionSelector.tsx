import { useState } from "react";
import type { ChatSession } from "@/types/chat";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MessageSquare, Plus, Trash2, ChevronDown, Loader2 } from "lucide-react";

interface SessionSelectorProps {
  sessions: ChatSession[];
  activeSession: ChatSession | null;
  isLoading?: boolean;
  onSelectSession: (session: ChatSession) => void;
  onNewSession: () => void;
  onDeleteSession: (sessionId: string) => void;
}

export function SessionSelector({
  sessions,
  activeSession,
  isLoading,
  onSelectSession,
  onNewSession,
  onDeleteSession,
}: SessionSelectorProps) {
  const [open, setOpen] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (diffDays === 0) return "Hoy";
    if (diffDays === 1) return "Ayer";
    if (diffDays < 7) return `Hace ${diffDays} días`;
    return date.toLocaleDateString();
  };

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="gap-2 max-w-[300px]">
          <MessageSquare className="h-4 w-4 shrink-0" />
          <span className="truncate">
            {activeSession ? activeSession.title : "Seleccionar conversación"}
          </span>
          <ChevronDown className="h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-[300px]">
        <DropdownMenuItem
          onClick={() => {
            onNewSession();
            setOpen(false);
          }}
          className="gap-2 text-primary"
        >
          <Plus className="h-4 w-4" />
          Nueva conversación
        </DropdownMenuItem>
        
        {sessions.length > 0 && <DropdownMenuSeparator />}
        
        {isLoading ? (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          </div>
        ) : sessions.length === 0 ? (
          <div className="text-center py-4 text-sm text-muted-foreground">
            No tienes conversaciones
          </div>
        ) : (
          <div className="max-h-[300px] overflow-y-auto">
            {sessions.map((session) => (
              <DropdownMenuItem
                key={session.id}
                onClick={() => {
                  onSelectSession(session);
                  setOpen(false);
                }}
                className="flex items-center justify-between gap-2 group"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{session.title}</p>
                  <p className="text-xs text-muted-foreground">
                    {session.subject} · {formatDate(session.last_active)}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 opacity-0 group-hover:opacity-100 shrink-0"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(session.id);
                  }}
                >
                  <Trash2 className="h-3 w-3 text-destructive" />
                </Button>
              </DropdownMenuItem>
            ))}
          </div>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
