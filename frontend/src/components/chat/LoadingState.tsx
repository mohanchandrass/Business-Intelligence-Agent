"use client";

import React, { useEffect, useRef, useState } from "react";
import { getLoadingStages } from "@/utils/loadingMessages";

interface LoadingStateProps {
  /** The user's current pending message — drives intent detection. */
  userMessage?: string;
}

export function LoadingState({ userMessage = "" }: LoadingStateProps) {
  const stages = getLoadingStages(userMessage);

  // stageIndex advances ONE WAY only — it never wraps back to 0.
  const [stageIndex, setStageIndex] = useState(0);
  // Fade flag for smooth text transitions between stages.
  const [visible, setVisible] = useState(true);

  // Keep a stable ref to the timeout so we can cancel it on unmount or re-render.
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearTimer = () => {
    if (timerRef.current !== null) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  };

  // Reset to stage 0 whenever a new query starts (userMessage changes).
  useEffect(() => {
    clearTimer();
    setStageIndex(0);
    setVisible(true);
  }, [userMessage]);

  // Advance to the next stage after the current stage's minDurationMs.
  // If already at the last stage (minDurationMs === 0), do nothing — stay there.
  useEffect(() => {
    clearTimer();

    const currentStage = stages[stageIndex];
    if (!currentStage) return;

    const isLastStage = stageIndex >= stages.length - 1;
    if (isLastStage) return; // ← THE KEY: never advance past the final stage.

    const delay = currentStage.minDurationMs;
    if (delay <= 0) return; // safety guard — treat 0 as "stay here"

    timerRef.current = setTimeout(() => {
      // Fade out, then swap text, then fade back in.
      setVisible(false);
      timerRef.current = setTimeout(() => {
        setStageIndex((prev) => prev + 1);
        setVisible(true);
      }, 250); // cross-fade duration
    }, delay);

    return clearTimer;
  }, [stageIndex, stages]); // eslint-disable-line react-hooks/exhaustive-deps

  const currentText = stages[stageIndex]?.text ?? "";

  return (
    <div className="w-full flex justify-start mb-8">
      <div className="flex max-w-[85%] flex-row gap-4">
        {/* Avatar — matches assistant message style */}
        <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 bg-primary/10 text-primary border border-primary/20">
          <span className="text-[10px] font-bold select-none">AI</span>
        </div>

        <div className="flex flex-col items-start w-full bg-surface border border-border rounded-2xl rounded-tl-sm p-4 shadow-sm">
          <div className="flex items-center gap-3">

            {/* Bouncing dots — these animate continuously because they represent
                "still working", not "progressing through stages". */}
            <div className="flex gap-1" aria-hidden="true">
              <div className="w-1.5 h-1.5 bg-primary/50 rounded-full animate-bounce [animation-delay:-0.3s]" />
              <div className="w-1.5 h-1.5 bg-primary/50 rounded-full animate-bounce [animation-delay:-0.15s]" />
              <div className="w-1.5 h-1.5 bg-primary/50 rounded-full animate-bounce" />
            </div>

            {/* Stage label — fades between stage changes, then stays put. */}
            <span
              className="text-sm font-medium text-muted transition-opacity duration-[250ms]"
              style={{ opacity: visible ? 1 : 0 }}
              aria-live="polite"
              aria-label={`Loading: ${currentText}`}
            >
              {currentText}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
