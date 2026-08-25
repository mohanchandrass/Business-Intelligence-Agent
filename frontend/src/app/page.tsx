"use client";

import React from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { useChat } from "@/hooks/useChat";

export default function Home() {
  const { 
    messages, 
    isLoading, 
    pendingMessage,
    error, 
    sendMessage, 
    newConversation
  } = useChat();

  const handleRetry = () => {
    const lastUserMessage = [...messages].reverse().find(m => m.role === "user");
    if (lastUserMessage) {
      sendMessage(lastUserMessage.content);
    }
  };

  return (
    <AppShell onNewChat={newConversation}>
      <ChatContainer
        messages={messages}
        isLoading={isLoading}
        pendingMessage={pendingMessage}
        error={error}
        onSendMessage={sendMessage}
        onRetry={handleRetry}
      />
    </AppShell>
  );
}
