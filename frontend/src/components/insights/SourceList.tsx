import React from "react";
import { Citation } from "@/contracts/api";
import { Link } from "lucide-react";

interface SourceListProps {
  citations: Citation[];
}

export function SourceList({ citations }: SourceListProps) {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-6 pt-4 border-t border-border">
      <h4 className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">
        Sources
      </h4>
      <div className="flex flex-wrap gap-2">
        {citations.map((citation, idx) => (
          <div
            key={idx}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-background border border-border text-xs text-foreground hover:bg-muted/5 transition-colors"
          >
            <Link className="w-3 h-3 text-muted" />
            <span>{citation.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
