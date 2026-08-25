import React, { useCallback, useEffect, useRef, useState } from "react";
import { ChatMessage as ChatMessageType } from "@/contracts/api";
import { ChatMessage } from "./ChatMessage";
import { EmptyState } from "./EmptyState";
import { LoadingState } from "./LoadingState";
import { ChatComposer } from "./ChatComposer";

interface ChatContainerProps {
  messages: ChatMessageType[];
  isLoading: boolean;
  pendingMessage?: string;
  error: string | null;
  onSendMessage: (msg: string) => void;
  onRetry: () => void;
}

export function ChatContainer({
  messages,
  isLoading,
  pendingMessage = "",
  error,
  onSendMessage,
  onRetry,
}: ChatContainerProps) {
  // The scrollable viewport — we target this for scroll-position reads.
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  // Invisible sentinel pinned to the bottom of the message list.
  const bottomRef = useRef<HTMLDivElement>(null);
  // Track previous message count so we can detect *new* messages.
  const prevLengthRef = useRef(messages.length);
  // Whether the user has intentionally scrolled up — suppresses auto-scroll.
  const [userScrolledUp, setUserScrolledUp] = useState(false);

  // ── Auto-scroll logic ───────────────────────────────────────────────────────
  // We only auto-scroll in three cases:
  //  1. A genuinely new message was appended.
  //  2. The loading state appeared (isLoading flipped to true).
  //  3. The user is already near the bottom (≤ 120 px) — safe to keep them there.
  // In all other cases we leave the viewport alone so the user can read history.

  const scrollToBottom = useCallback((behaviour: ScrollBehavior = "smooth") => {
    bottomRef.current?.scrollIntoView({ behavior: behaviour, block: "end" });
  }, []);

  // Detect user-initiated upward scroll.
  const handleScroll = useCallback(() => {
    const el = scrollAreaRef.current;
    if (!el) return;
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    // If more than 120 px from the bottom, the user has scrolled up deliberately.
    setUserScrolledUp(distanceFromBottom > 120);
  }, []);

  useEffect(() => {
    const el = scrollAreaRef.current;
    if (!el) return;
    el.addEventListener("scroll", handleScroll, { passive: true });
    return () => el.removeEventListener("scroll", handleScroll);
  }, [handleScroll]);

  useEffect(() => {
    const isNewMessage = messages.length > prevLengthRef.current;
    prevLengthRef.current = messages.length;

    if (isNewMessage || !userScrolledUp) {
      // New message always scrolls; otherwise only scroll if already near bottom.
      scrollToBottom(isNewMessage ? "smooth" : "smooth");
    }
  }, [messages, isLoading, error, userScrolledUp, scrollToBottom]);

  // When loading starts for a brand-new message, always pull down.
  const prevIsLoadingRef = useRef(isLoading);
  useEffect(() => {
    if (isLoading && !prevIsLoadingRef.current) {
      // Loading just started — snap to bottom so the indicator is visible.
      scrollToBottom("smooth");
      setUserScrolledUp(false);
    }
    prevIsLoadingRef.current = isLoading;
  }, [isLoading, scrollToBottom]);

  return (
    // Outer: fills the parent (main in AppShell), laid out as a flex column.
    // The flex-col structure means the composer occupies real layout space —
    // it is NOT absolutely positioned, so it never overlaps messages.
    <div className="flex flex-col h-full w-full">

      {/* ── Scrollable message viewport ───────────────────────────────────── */}
      {/* flex-1 + min-h-0 is the correct pattern for a flex child that must
          scroll. Without min-h-0 flex children grow to their content size and
          overflow-y: auto has nothing to clip. */}
      <div
        ref={scrollAreaRef}
        className="flex-1 min-h-0 overflow-y-auto"
      >
        <div className="max-w-4xl mx-auto w-full px-4 md:px-8 pt-8 pb-6 flex flex-col">
          {messages.length === 0 && !isLoading ? (
            <EmptyState onSelectPrompt={onSendMessage} />
          ) : (
            <>
              {messages.map((msg) => (
                <ChatMessage
                  key={msg.id}
                  message={msg}
                  onFollowUp={onSendMessage}
                />
              ))}

              {isLoading && <LoadingState userMessage={pendingMessage} />}

              {error && (
                <div className="w-full flex justify-center my-6">
                  <div className="bg-red/10 border border-red/20 rounded-xl p-4 flex flex-col items-center max-w-md w-full">
                    <p className="text-red font-medium text-sm mb-3 text-center">{error}</p>
                    <button
                      onClick={onRetry}
                      className="px-4 py-1.5 bg-red text-white text-sm font-medium rounded-md hover:bg-red/90 transition-colors"
                    >
                      Retry
                    </button>
                  </div>
                </div>
              )}

              {/* Bottom sentinel — scrollIntoView targets this. */}
              <div ref={bottomRef} className="h-1 shrink-0" aria-hidden="true" />
            </>
          )}
        </div>
      </div>

      {/* ── Composer footer ───────────────────────────────────────────────── */}
      {/* shrink-0 ensures the composer never gets squeezed by the scroll area.
          The gradient is part of the composer wrapper, not an overlay. */}
      <div className="shrink-0 w-full bg-gradient-to-t from-background via-background/95 to-transparent pt-2 pb-2">
        <ChatComposer onSend={onSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}
