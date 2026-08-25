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
    <div className="flex flex-col h-screen w-full bg-background overflow-hidden relative">
      {/* Universal Header */}
      <header className="flex items-center justify-between p-4 border-b border-border bg-surface shrink-0 z-10">
        <h1 className="text-lg font-semibold text-foreground tracking-tight">Skylark BI</h1>
        
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
      
      {/* Main Chat Area */}
      <main className="flex-1 w-full h-full relative overflow-hidden flex flex-col">
        {children}
      </main>

      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
    </div>
  );
}
