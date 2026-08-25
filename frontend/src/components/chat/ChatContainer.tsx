import React, { useEffect, useRef } from "react";
import { ChatMessage as ChatMessageType } from "@/contracts/api";
import { ChatMessage } from "./ChatMessage";
import { EmptyState } from "./EmptyState";
import { LoadingState } from "./LoadingState";
import { ChatComposer } from "./ChatComposer";

interface ChatContainerProps {
  messages: ChatMessageType[];
  isLoading: boolean;
  pendingMessage?: string;
  error: string | null;
  onSendMessage: (msg: string) => void;
  onRetry: () => void;
}

export function ChatContainer({ messages, isLoading, pendingMessage = "", error, onSendMessage, onRetry }: ChatContainerProps) {
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, error]);

  return (
    <div className="flex flex-col h-full w-full relative">
      <div className="flex-1 overflow-y-auto px-4 md:px-8 pt-8 pb-32">
        <div className="max-w-4xl mx-auto w-full h-full flex flex-col">
          {messages.length === 0 && !isLoading ? (
            <EmptyState onSelectPrompt={onSendMessage} />
          ) : (
            <div className="w-full flex flex-col">
              {messages.map((msg) => (
                <ChatMessage 
                  key={msg.id} 
                  message={msg} 
                  onFollowUp={onSendMessage} 
                />
              ))}

              {isLoading && <LoadingState userMessage={pendingMessage} />}
              
              {error && (
                <div className="w-full flex justify-center my-6">
                  <div className="bg-red/10 border border-red/20 rounded-xl p-4 flex flex-col items-center max-w-md w-full">
                    <p className="text-red font-medium text-sm mb-3 text-center">{error}</p>
                    <button 
                      onClick={onRetry}
                      className="px-4 py-1.5 bg-red text-white text-sm font-medium rounded-md hover:bg-red/90 transition-colors"
                    >
                      Retry
                    </button>
                  </div>
                </div>
              )}
              
              <div ref={endOfMessagesRef} className="h-4" />
            </div>
          )}
        </div>
      </div>

      <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-background via-background to-transparent pt-6 pb-2">
        <ChatComposer onSend={onSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}
