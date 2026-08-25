import { useState, useCallback } from "react";
import { ChatMessage, ChatRequest } from "@/contracts/api";
import { chatService } from "@/services/chatService";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [pendingMessage, setPendingMessage] = useState<string>("");

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return;

    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      role: "user",
      content: text,
      createdAt: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setPendingMessage(text);
    setError(null);

    try {
      const request: ChatRequest = {
        message: text,
        conversation_id: conversationId,
      };

      const response = await chatService.sendMessage(request);
      
      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      const assistantMessage: ChatMessage = {
        id: `msg_${Date.now() + 1}`,
        role: "assistant",
        content: response.answer,
        response: response,
        createdAt: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
      setPendingMessage("");
    }
  }, [conversationId]);

  const newConversation = useCallback(() => {
    setMessages([]);
    setConversationId(undefined);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    pendingMessage,
    error,
    sendMessage,
    newConversation,
  };
}
