import React, { useEffect, useState } from "react";
import { X, CheckCircle2, XCircle, HelpCircle } from "lucide-react";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline" | "not_checked">("not_checked");
  
  const isMock = process.env.NEXT_PUBLIC_USE_MOCK_API === "true";
  const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  useEffect(() => {
    if (isOpen && !isMock) {
      setBackendStatus("checking");
      fetch(`${backendUrl}/api/v1/health`)
        .then(res => {
          if (res.ok) setBackendStatus("online");
          else setBackendStatus("offline");
        })
        .catch(() => setBackendStatus("offline"));
    }
  }, [isOpen, backendUrl, isMock]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/20 backdrop-blur-sm">
      <div className="bg-surface border border-border rounded-2xl shadow-lg w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-lg font-semibold text-foreground">Settings</h2>
          <button 
            onClick={onClose}
            className="p-1 rounded-md text-muted hover:bg-background transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Monday.com section */}
          <div>
            <h3 className="text-sm font-semibold text-muted uppercase tracking-wider mb-3">
              Monday.com
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center text-sm">
                <span className="text-foreground font-medium">Connection</span>
                <div className="flex items-center gap-1.5 text-muted">
                  <HelpCircle className="w-4 h-4" />
                  <span>Not configured</span>
                </div>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-foreground font-medium">Workspace</span>
                <span className="text-muted">Skylark Drones</span>
              </div>
              <div className="space-y-2 mt-2">
                <span className="text-sm text-foreground font-medium">Data access</span>
                <div className="flex items-center gap-2 text-sm text-muted">
                  <CheckCircle2 className="w-4 h-4 text-green" /> Deals
                </div>
                <div className="flex items-center gap-2 text-sm text-muted">
                  <CheckCircle2 className="w-4 h-4 text-green" /> Work Orders
                </div>
              </div>
            </div>
          </div>

          <div className="w-full h-px bg-border"></div>

          {/* Backend section */}
          <div>
            <h3 className="text-sm font-semibold text-muted uppercase tracking-wider mb-3">
              Backend
            </h3>
            <div className="space-y-3">
              <div className="flex flex-col gap-1 text-sm">
                <span className="text-foreground font-medium">API</span>
                <span className="text-muted font-mono bg-background p-1.5 rounded text-xs truncate">
                  {backendUrl}
                </span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-foreground font-medium">Status</span>
                <div className="flex items-center gap-1.5">
                  {isMock ? (
                    <span className="text-muted">N/A (Mock Mode)</span>
                  ) : backendStatus === "checking" ? (
                    <span className="text-muted">Checking...</span>
                  ) : backendStatus === "online" ? (
                    <><div className="w-2 h-2 rounded-full bg-green"></div><span className="text-green font-medium">Online</span></>
                  ) : backendStatus === "offline" ? (
                    <><XCircle className="w-4 h-4 text-red" /><span className="text-red font-medium">Offline</span></>
                  ) : (
                    <span className="text-muted">Not checked</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="w-full h-px bg-border"></div>

          {/* Environment section */}
          <div>
            <h3 className="text-sm font-semibold text-muted uppercase tracking-wider mb-3">
              Environment
            </h3>
            <div className="flex justify-between items-center text-sm">
              <span className="text-foreground font-medium">Mode</span>
              <span className="px-2 py-1 bg-background border border-border rounded font-mono text-xs text-primary">
                {isMock ? "Mock" : "API"}
              </span>
            </div>
          </div>
        </div>
        
        <div className="p-4 border-t border-border flex justify-end bg-background/50">
          <button 
            onClick={onClose}
            className="px-4 py-2 bg-primary text-white text-sm font-medium rounded-md hover:bg-primary/90 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
