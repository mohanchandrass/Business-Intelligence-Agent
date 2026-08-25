import React, { useRef, useEffect } from "react";
import { SendHorizontal } from "lucide-react";

interface ChatComposerProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatComposer({ onSend, disabled }: ChatComposerProps) {
  const [text, setText] = React.useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [text]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (text.trim() && !disabled) {
        onSend(text);
        setText("");
      }
    }
  };

  const handleSend = () => {
    if (text.trim() && !disabled) {
      onSend(text);
      setText("");
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-4">
      <div className="relative flex items-end w-full rounded-2xl border border-border bg-surface shadow-sm focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about pipeline, deals, work orders..."
          className="w-full max-h-[200px] min-h-[56px] py-4 pl-4 pr-12 bg-transparent outline-none resize-none text-foreground placeholder:text-muted"
          rows={1}
          disabled={disabled}
        />
        <button
          onClick={handleSend}
          disabled={!text.trim() || disabled}
          className="absolute right-2 bottom-2 p-2 rounded-xl text-primary hover:bg-primary/10 disabled:text-muted disabled:hover:bg-transparent transition-colors flex items-center justify-center h-10 w-10"
        >
          <SendHorizontal className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
