import React, { useState } from "react";
import { SettingsModal } from "./SettingsModal";
import { Settings, Plus } from "lucide-react";

interface AppShellProps {
  children: React.ReactNode;
  onNewChat: () => void;
}

export function AppShell({ children, onNewChat }: AppShellProps) {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  return (
    <div className="flex flex-col h-screen w-full bg-background overflow-hidden">
      {/* Universal Header */}
      <header className="flex items-center justify-between p-4 border-b border-border bg-surface shrink-0 z-10">
        <h1 
          className="text-lg font-semibold text-foreground tracking-tight cursor-pointer hover:text-primary transition-colors"
          onClick={onNewChat}
          title="Return to Home"
        >
          Skylark BI
        </h1>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={onNewChat}
            className="flex items-center gap-1.5 px-3 py-1.5 text-primary bg-primary/10 hover:bg-primary/20 rounded-md font-medium text-sm transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>New Chat</span>
          </button>
          
          <button 
            onClick={() => setIsSettingsOpen(true)}
            className="p-2 text-muted hover:text-foreground hover:bg-background rounded-md transition-colors"
            title="Settings"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </header>
      
      {/* Main Chat Area — flex-1 gives it all remaining height after the header.
          overflow-hidden clips children while flex-col+h-full propagates a
          definite height down to ChatContainer so its scroll area can work. */}
      <main className="flex-1 min-h-0 w-full overflow-hidden flex flex-col">
        {children}
      </main>

      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
    </div>
  );
}
