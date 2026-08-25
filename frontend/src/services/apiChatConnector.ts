import { ChatRequest, ChatResponse } from "@/contracts/api";

export class ApiChatConnector {
  private baseUrl: string;

  constructor() {
    const defaultUrl = process.env.NODE_ENV === "production" ? "https://business-intelligence-agent-yzpi.onrender.com" : "http://localhost:8000";
    this.baseUrl = process.env.VITE_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || defaultUrl;
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    console.log("[Skylark Chat]");
    console.log(`POST ${this.baseUrl}/api/v1/chat`);
    console.log("");
    console.log("[Skylark Chat]");
    console.log("Request:\n" + JSON.stringify(request, null, 2));

    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      console.log("[Skylark Chat]");
      console.log(`Response status: ${response.status}`);

      if (!response.ok) {
        return this.getFallbackErrorResponse(request.conversation_id, response.statusText);
      }

      const data = await response.json();
      console.log("[Skylark Chat]");
      console.log("Response data:\n" + JSON.stringify(data, null, 2));
      return data;
    } catch (e: any) {
      console.error("[Skylark Chat] Network Error:", e);
      return this.getFallbackErrorResponse(request.conversation_id, e.message);
    }
  }

  private getFallbackErrorResponse(convId: string | undefined, message: string): ChatResponse {
    return {
      conversation_id: convId || `conv_${Date.now()}`,
      answer: `Unable to reach the Skylark BI backend.\n\nMake sure the backend is running at:\nhttp://localhost:8000\n\nError: ${message}`,
      metadata: {
        execution_time_ms: 0,
      },
    };
  }
}
