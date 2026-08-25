export interface ChatRequest {
  message: string;
  conversation_id?: string;
  context?: Record<string, unknown>;
}

export type VisualizationType = "kpi" | "bar" | "line" | "progress" | "table" | "donut";

export interface VisualizationData {
  type: VisualizationType;
  title: string;
  [key: string]: any;
}

export interface KpiVisualization extends VisualizationData {
  type: "kpi";
  value: string;
  change?: string;
  change_direction?: "up" | "down" | "neutral";
  description?: string;
}

export interface BarVisualization extends VisualizationData {
  type: "bar";
  data: Array<{
    label: string;
    value: number;
  }>;
  unit?: string;
}

export interface LineVisualization extends VisualizationData {
  type: "line";
  data: Array<{
    label: string;
    value: number;
  }>;
  unit?: string;
}

export interface ProgressVisualization extends VisualizationData {
  type: "progress";
  data: Array<{
    label: string;
    value: number;
  }>;
}

export interface TableVisualization extends VisualizationData {
  type: "table";
  columns: string[];
  data: Array<Record<string, any>>;
}

export interface Insight {
  title?: string;
  description: string;
}

export interface Citation {
  text: string;
  url?: string;
}

export interface DataQualityIssue {
  severity: "info" | "warning" | "error";
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  insights?: Insight[];
  data?: VisualizationData[];
  citations?: Citation[];
  data_quality?: DataQualityIssue[];
  follow_up_questions?: string[];
  metadata?: {
    execution_time_ms?: number;
    tools_used?: string[];
  };
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
  createdAt: string;
}

export interface ConversationSummary {
  id: string;
  title: string;
  updatedAt: string;
}

