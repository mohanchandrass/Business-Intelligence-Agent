import React from "react";
import { cn } from "@/lib/utils";
import { ConversationSummary } from "@/contracts/api";
import { Settings } from "lucide-react";

interface SidebarProps {
  onNewChat: () => void;
  recentConversations: ConversationSummary[];
  onSelectConversation: (id: string) => void;
  activeConversationId?: string;
  onOpenSettings: () => void;
  className?: string;
}

export function Sidebar({ 
  onNewChat, 
  recentConversations, 
  onSelectConversation,
  activeConversationId,
  onOpenSettings,
  className 
}: SidebarProps) {
  return (
    <aside
      className={cn(
        "flex flex-col h-full bg-surface border-r border-border w-64 p-4 shrink-0",
        className
      )}
    >
      <div className="flex items-center mb-8">
        <h1 className="text-xl font-semibold text-foreground tracking-tight">Skylark BI</h1>
      </div>

      <button
        onClick={onNewChat}
        className="flex items-center justify-center gap-2 w-full bg-primary text-white py-2 px-4 rounded-md hover:bg-primary/90 transition-colors font-medium mb-8"
      >
        <span>+</span> New conversation
      </button>

      {recentConversations.length > 0 && (
        <div className="flex-1 overflow-y-auto">
          <h2 className="text-xs font-semibold text-muted uppercase tracking-wider mb-4">
            Recent
          </h2>
          <ul className="space-y-1">
            {recentConversations.map(conv => (
              <li 
                key={conv.id}
                onClick={() => onSelectConversation(conv.id)}
                className={cn(
                  "text-sm px-3 py-2 rounded-md cursor-pointer truncate transition-colors",
                  activeConversationId === conv.id 
                    ? "bg-primary/10 text-primary font-medium" 
                    : "text-foreground hover:bg-background"
                )}
                title={conv.title}
              >
                {conv.title}
              </li>
            ))}
          </ul>
        </div>
      )}

      {recentConversations.length === 0 && (
        <div className="flex-1"></div>
      )}

      <div className="pt-4 border-t border-border mt-auto">
        <button 
          onClick={onOpenSettings}
          className="flex items-center gap-2 text-sm text-muted cursor-pointer hover:text-foreground w-full py-2 px-1 rounded hover:bg-background transition-colors"
        >
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </button>
      </div>
    </aside>
  );
}
