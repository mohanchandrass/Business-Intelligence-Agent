import { ChatRequest, ChatResponse } from "@/contracts/api";
import { MockChatConnector } from "./mockChatConnector";
import { ApiChatConnector } from "./apiChatConnector";

export interface ChatConnector {
  sendMessage(request: ChatRequest): Promise<ChatResponse>;
}

class ChatService implements ChatConnector {
  private connector: ChatConnector;
  private isMock: boolean;

  constructor() {
    this.isMock = process.env.NEXT_PUBLIC_USE_MOCK_API === "true";
    this.connector = this.isMock ? new MockChatConnector() : new ApiChatConnector();
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    console.log("[Skylark Chat]");
    console.log("User message:", request.message);
    console.log("");
    console.log("[Skylark Chat]");
    console.log(`Connector: ${this.isMock ? 'MockChatConnector' : 'ApiChatConnector'}`);
    
    return this.connector.sendMessage(request);
  }
}

export const chatService = new ChatService();
