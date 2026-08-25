import React from "react";
import { MessageCircleQuestion } from "lucide-react";

interface FollowUpChipsProps {
  questions: string[];
  onSelect: (question: string) => void;
}

export function FollowUpChips({ questions, onSelect }: FollowUpChipsProps) {
  if (!questions || questions.length === 0) return null;

  return (
    <div className="mt-6">
      <p className="text-sm text-muted mb-3">You may also want to ask:</p>
      <div className="flex flex-wrap gap-2">
        {questions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => onSelect(q)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface border border-primary/30 text-primary text-sm hover:bg-primary hover:text-white transition-colors text-left"
          >
            <MessageCircleQuestion className="w-4 h-4 shrink-0" />
            <span>{q}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
