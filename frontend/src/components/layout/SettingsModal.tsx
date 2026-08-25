import React, { useEffect, useState } from "react";
import { X } from "lucide-react";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface StatusData {
  backend: {
    status: string;
  };
  monday: {
    configured: boolean;
    connected: boolean;
  };
  environment: {
    mode: string;
  };
}

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [statusData, setStatusData] = useState<StatusData | null>(null);

  const isMock = process.env.NEXT_PUBLIC_USE_MOCK_API === "true";
  const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  useEffect(() => {
    if (!isOpen) return;

    if (isMock) {
      setBackendStatus("offline");
      setStatusData(null);
      return;
    }

    setBackendStatus("checking");
    fetch(`${backendUrl}/api/v1/status`)
      .then(async (res) => {
        if (res.ok) {
          const data = await res.json();
          setStatusData(data);
          setBackendStatus("online");
        } else {
          setBackendStatus("offline");
          setStatusData(null);
        }
      })
      .catch(() => {
        setBackendStatus("offline");
        setStatusData(null);
      });
  }, [isOpen, backendUrl, isMock]);

  if (!isOpen) return null;

  // Resolve Monday status text & colors
  let mondayText = "Not configured";
  let mondayDotColor = "bg-muted";

  if (isMock) {
    mondayText = "Not configured";
    mondayDotColor = "bg-muted";
  } else if (backendStatus === "checking") {
    mondayText = "Checking...";
    mondayDotColor = "bg-muted animate-pulse";
  } else if (backendStatus === "offline") {
    mondayText = "Unavailable";
    mondayDotColor = "bg-red";
  } else if (statusData) {
    if (statusData.monday.configured) {
      if (statusData.monday.connected) {
        mondayText = "Connected";
        mondayDotColor = "bg-green";
      } else {
        mondayText = "Unavailable";
        mondayDotColor = "bg-red";
      }
    } else {
      mondayText = "Not configured";
      mondayDotColor = "bg-muted";
    }
  }

  // Resolve Backend Status text & colors
  let backendText = "Offline";
  let backendDotColor = "bg-red";

  if (isMock) {
    backendText = "Offline";
    backendDotColor = "bg-red";
  } else if (backendStatus === "checking") {
    backendText = "Checking...";
    backendDotColor = "bg-muted animate-pulse";
  } else if (backendStatus === "online") {
    backendText = "Online";
    backendDotColor = "bg-green";
  }

  // Resolve Environment Mode
  const modeText = isMock ? "Mock" : "API";
  const isProduction = process.env.NODE_ENV === "production";

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
          {/* Monday.com Section */}
          <div>
            <h3 className="text-sm font-semibold text-muted uppercase tracking-wider mb-3">
              Monday.com
            </h3>
            <div className="flex justify-between items-center text-sm">
              <span className="text-foreground font-medium">Connection</span>
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${mondayDotColor}`}></span>
                <span className="text-foreground font-medium">{mondayText}</span>
              </div>
            </div>
          </div>

          <div className="w-full h-px bg-border"></div>

          {/* Backend Section */}
          <div>
            <h3 className="text-sm font-semibold text-muted uppercase tracking-wider mb-3">
              Backend
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="text-foreground font-medium">API</span>
                <span className="text-muted font-mono text-xs">
                  {backendUrl}
                </span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-foreground font-medium">Status</span>
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${backendDotColor}`}></span>
                  <span className="text-foreground font-medium">{backendText}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Environment Section (hidden in production) */}
          {!isProduction && (
            <>
              <div className="w-full h-px bg-border"></div>
              <div>
                <h3 className="text-sm font-semibold text-muted uppercase tracking-wider mb-3">
                  Environment
                </h3>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-foreground font-medium">Mode</span>
                  <span className="px-2 py-1 bg-background border border-border rounded font-mono text-xs text-primary font-medium">
                    {modeText}
                  </span>
                </div>
              </div>
            </>
          )}
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
