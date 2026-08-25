"use client";

import React, { useEffect, useState } from "react";
import { getLoadingMessages } from "@/utils/loadingMessages";

interface LoadingStateProps {
  /** The user's current pending message — used to pick context-aware copy. */
  userMessage?: string;
}

const ROTATION_INTERVAL_MS = 2800;

export function LoadingState({ userMessage = "" }: LoadingStateProps) {
  const messages = getLoadingMessages(userMessage);
  const [index, setIndex] = useState(0);
  const [visible, setVisible] = useState(true);

  // Rotate through messages with a gentle fade
  useEffect(() => {
    setIndex(0);
    setVisible(true);

    const intervalId = setInterval(() => {
      // Fade out
      setVisible(false);
      setTimeout(() => {
        setIndex((prev) => (prev + 1) % messages.length);
        setVisible(true);
      }, 300); // fade-out duration
    }, ROTATION_INTERVAL_MS);

    return () => clearInterval(intervalId);
  }, [userMessage, messages.length]);

  return (
    <div className="w-full flex justify-start mb-8">
      <div className="flex max-w-[85%] flex-row gap-4">
        {/* Avatar dot — matches assistant message style */}
        <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 bg-primary/10 text-primary border border-primary/20">
          <span className="text-[10px] font-bold select-none">AI</span>
        </div>

        <div className="flex flex-col items-start w-full bg-surface border border-border rounded-2xl rounded-tl-sm p-4 shadow-sm">
          <div className="flex items-center gap-3">
            {/* Animated dot trio */}
            <div className="flex gap-1" aria-hidden="true">
              <div className="w-1.5 h-1.5 bg-primary/50 rounded-full animate-bounce [animation-delay:-0.3s]" />
              <div className="w-1.5 h-1.5 bg-primary/50 rounded-full animate-bounce [animation-delay:-0.15s]" />
              <div className="w-1.5 h-1.5 bg-primary/50 rounded-full animate-bounce" />
            </div>

            {/* Rotating context-aware label */}
            <span
              className="text-sm font-medium text-muted transition-opacity duration-300"
              style={{ opacity: visible ? 1 : 0 }}
            >
              {messages[index]}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
