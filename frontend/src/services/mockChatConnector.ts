import { ChatRequest, ChatResponse, VisualizationData } from "@/contracts/api";

export class MockChatConnector {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const msg = request.message.toLowerCase().trim();

    // 1. Pipeline Scenario
    if (msg.includes("pipeline") || msg.includes("deals pipeline") || msg.includes("pipeline looking")) {
      return this.getPipelineScenario(request.conversation_id);
    }
    
    // 2. Work Order Scenario
    if (msg.includes("work order") || msg.includes("at risk") || msg.includes("risk") || msg.includes("delayed")) {
      return this.getAtRiskScenario(request.conversation_id);
    }
    
    // 3. Cross-board Scenario
    if (msg.includes("compare") || msg.includes("vs") || msg.includes("cross board")) {
      return this.getCrossBoardScenario(request.conversation_id);
    }

    // 4. Clarification Scenario
    if (msg.includes("how is the business") || msg.includes("how are we doing") || msg.includes("business update") || msg.includes("what's happening")) {
      return this.getClarificationScenario(request.conversation_id);
    }
    
    // 5. Greeting Scenario
    if (["hi", "hello", "hey", "good morning", "good afternoon", "good evening"].includes(msg)) {
      return {
        conversation_id: request.conversation_id || `conv_${Date.now()}`,
        answer: "Hi! I'm Skylark BI.\n\nI can help you analyze pipeline, deals, work orders, sector performance, revenue and operational metrics from your Monday.com data.\n\nWhat would you like to know?"
      };
    }
    
    // 6. Basic Identity
    if (msg.includes("what are you") || msg.includes("who are you") || msg.includes("what can you do") || msg.includes("help")) {
      return {
        conversation_id: request.conversation_id || `conv_${Date.now()}`,
        answer: "I'm Skylark BI, a business intelligence assistant.\n\nI can analyze your Monday.com work orders and deals to answer questions about:\n\n• Sales pipeline\n• Revenue\n• Sector performance\n• Work-order execution\n• Operational risks\n• Cross-board performance\n\nTry asking:\n\"How's our pipeline looking this quarter?\""
      };
    }

    // Default graceful fallback scenario
    return {
      conversation_id: request.conversation_id || `conv_${Date.now()}`,
      answer: "I'm not sure what business question you're asking.\n\nTry asking about pipeline, deals, work orders, revenue or sector performance.",
      metadata: {
        execution_time_ms: 50,
      }
    };
  }

  private getPipelineScenario(convId?: string): ChatResponse {
    return {
      conversation_id: convId || `conv_${Date.now()}`,
      answer: "The energy sector currently has ₹4.8Cr in active pipeline across 12 deals.",
      data: [
        {
          type: "kpi",
          title: "Pipeline",
          value: "₹4.8 Cr",
          change: "12%",
          change_direction: "up",
        },
        {
          type: "kpi",
          title: "Deals",
          value: "12",
        },
        {
          type: "kpi",
          title: "Win Rate",
          value: "42%",
          change: "5%",
          change_direction: "down",
        },
        {
          type: "bar",
          title: "Pipeline by Sector",
          data: [
            { label: "Energy", value: 48000000 },
            { label: "Mining", value: 32000000 },
            { label: "Infrastructure", value: 21000000 },
          ],
          unit: "INR",
        }
      ],
      insights: [
        { description: "Energy represents 31% of total pipeline." },
        { description: "₹1.4Cr is currently in negotiation." },
        { description: "3 deals have been inactive for more than 30 days." }
      ],
      data_quality: [
        {
          severity: "warning",
          message: "2 deals have missing expected close dates, so timeline analysis excludes those records."
        }
      ],
      citations: [
        { text: "Monday.com · Deals board" }
      ],
      follow_up_questions: [
        "Which energy deals are closest to closing?",
        "Compare with mining"
      ]
    };
  }

  private getAtRiskScenario(convId?: string): ChatResponse {
    return {
      conversation_id: convId || `conv_${Date.now()}`,
      answer: "There are currently 3 work orders marked as 'At Risk' or 'Delayed'.",
      data: [
        {
          type: "kpi",
          title: "At-Risk Projects",
          value: "3",
          description: "Requires immediate attention"
        },
        {
          type: "table",
          title: "At-Risk Work Orders",
          columns: ["Project", "Owner", "Status", "Delay"],
          data: [
            { Project: "Solar Farm Alpha", Owner: "Ravi", Status: "Blocked", Delay: "12 days" },
            { Project: "Wind Project B", Owner: "Priya", Status: "At Risk", Delay: "7 days" },
            { Project: "Energy Survey C", Owner: "Arun", Status: "Delayed", Delay: "5 days" },
          ]
        }
      ],
      insights: [
        { description: "Solar Farm Alpha has been blocked for nearly two weeks." }
      ],
      citations: [
        { text: "Monday.com · Work Orders" }
      ]
    };
  }

  private getCrossBoardScenario(convId?: string): ChatResponse {
    return {
      conversation_id: convId || `conv_${Date.now()}`,
      answer: "The energy pipeline is strong at ₹4.8Cr, but current energy work orders are showing signs of strain with 2 projects delayed.",
      data: [
        {
          type: "kpi",
          title: "Energy Pipeline",
          value: "₹4.8 Cr"
        },
        {
          type: "kpi",
          title: "Energy Work Orders",
          value: "14 Active",
          description: "2 delayed"
        },
        {
          type: "bar",
          title: "Comparison",
          data: [
            { label: "Pipeline (Deals)", value: 12 },
            { label: "Active (Work Orders)", value: 14 }
          ]
        }
      ],
      data_quality: [
        {
          severity: "info",
          message: "Cross-board matching relies on the 'Sector' column matching exactly."
        }
      ]
    };
  }

  private getClarificationScenario(convId?: string): ChatResponse {
    return {
      conversation_id: convId || `conv_${Date.now()}`,
      answer: "Which area would you like to focus on?",
      follow_up_questions: [
        "Sales pipeline",
        "Work orders",
        "Sector performance"
      ]
    };
  }
}
