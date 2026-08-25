import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChatMessage as ChatMessageType } from "@/contracts/api";
import { VisualizationRenderer } from "../visualizations/VisualizationRenderer";
import { DataQualityAlert } from "../insights/DataQualityAlert";
import { SourceList } from "../insights/SourceList";
import { FollowUpChips } from "../insights/FollowUpChips";
import { Bot, User } from "lucide-react";

interface ChatMessageProps {
  message: ChatMessageType;
  onFollowUp: (question: string) => void;
}

export function ChatMessage({ message, onFollowUp }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`w-full flex ${isUser ? "justify-end" : "justify-start"} mb-8`}>
      <div
        className={`flex max-w-full lg:max-w-[85%] ${
          isUser ? "flex-row-reverse" : "flex-row"
        } gap-4 min-w-0`}
      >
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${
            isUser ? "bg-primary text-white" : "bg-primary/10 text-primary border border-primary/20"
          }`}
        >
          {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
        </div>
        
        <div
          className={`flex flex-col min-w-0 ${
            isUser
              ? "items-end"
              : "items-start bg-surface border border-border rounded-2xl rounded-tl-sm p-5 shadow-sm"
          }`}
        >
          {/* Main text content */}
          {isUser ? (
            <div className="bg-primary text-white px-5 py-3 rounded-2xl rounded-tr-sm whitespace-pre-wrap">
              {message.content}
            </div>
          ) : (
            <div className="prose prose-sm prose-slate max-w-full w-full mb-2 break-words">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}

          {/* Assistant specific structured data */}
          {!isUser && message.response && (
            <div className="w-full min-w-0 mt-2">
              {/* Insights section if any */}
              {message.response.insights && message.response.insights.length > 0 && (
                <div className="mb-4 bg-muted/5 p-4 rounded-xl border border-border">
                  <h4 className="text-xs font-semibold text-muted uppercase tracking-wider mb-2">
                    Key Insights
                  </h4>
                  <ul className="list-disc pl-5 space-y-1 text-sm text-foreground">
                    {message.response.insights.map((insight, idx) => (
                      <li key={idx}>
                        {insight.title && <span className="font-medium">{insight.title}: </span>}
                        {insight.description}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Visualizations */}
              {message.response.data && (
                <VisualizationRenderer data={message.response.data} />
              )}

              {/* Data Quality Alerts */}
              {message.response.data_quality && (
                <DataQualityAlert issues={message.response.data_quality} />
              )}

              {/* Sources */}
              {message.response.citations && (
                <SourceList citations={message.response.citations} />
              )}

              {/* Follow ups */}
              {message.response.follow_up_questions && (
                <FollowUpChips 
                  questions={message.response.follow_up_questions} 
                  onSelect={onFollowUp} 
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
