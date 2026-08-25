import React from "react";
import { Bot } from "lucide-react";

interface EmptyStateProps {
  onSelectPrompt: (prompt: string) => void;
}

export function EmptyState({ onSelectPrompt }: EmptyStateProps) {
  const prompts = [
    {
      category: "Pipeline",
      question: "How's our pipeline looking this quarter?"
    },
    {
      category: "Operations",
      question: "Which work orders are currently at risk?"
    },
    {
      category: "Performance",
      question: "Which sectors have the most active deals?"
    }
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full max-w-3xl mx-auto px-4 w-full">
      <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mb-6 text-primary">
        <Bot className="w-8 h-8" />
      </div>
      
      <h2 className="text-2xl font-bold text-foreground mb-2 text-center">
        Skylark BI
      </h2>
      <p className="text-muted text-center mb-10 text-lg max-w-md">
        Business intelligence from your Monday.com workspace. Ask questions, get answers, make decisions.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
        {prompts.map((p, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPrompt(p.question)}
            className="flex flex-col text-left p-5 rounded-2xl border border-border bg-surface hover:border-primary/50 hover:shadow-md transition-all h-full"
          >
            <span className="text-xs font-bold uppercase tracking-wider text-primary mb-3">
              {p.category}
            </span>
            <span className="text-sm font-medium text-foreground leading-relaxed">
              &quot;{p.question}&quot;
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
