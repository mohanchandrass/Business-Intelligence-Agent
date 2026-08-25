/**
 * One-way loading stage machine.
 *
 * Intent detection picks a sequence of stages tailored to the query.
 * The component advances through them with timeouts and STOPS at the last
 * stage — it never cycles back.
 *
 * Structure is intentionally exposed so the backend can later push real stage
 * updates (e.g. via SSE) without requiring a redesign here.
 */

// ─── Types ────────────────────────────────────────────────────────────────────

export interface LoadingStage {
  /** Human-readable label shown in the UI. */
  text: string;
  /**
   * Minimum time (ms) to display this stage before advancing to the next one.
   * The LAST stage in a sequence has no minimum — the component waits there
   * indefinitely until the response arrives.
   */
  minDurationMs: number;
}

export type IntentCategory =
  | "greeting"
  | "general"
  | "business"
  | "pipeline"
  | "work_order"
  | "cross_board";

// ─── Stage Sequences ──────────────────────────────────────────────────────────
// Each sequence is ONE-WAY only: A → B → C (then stay at C).

const STAGES: Record<IntentCategory, LoadingStage[]> = {
  greeting: [
    { text: "Thinking...", minDurationMs: 0 },
    // Single stage — stays here for simple conversational messages.
  ],

  general: [
    { text: "Thinking...", minDurationMs: 1500 },
    { text: "Understanding your request...", minDurationMs: 0 },
  ],

  business: [
    { text: "Thinking...", minDurationMs: 1500 },
    { text: "Understanding your request...", minDurationMs: 1800 },
    { text: "Preparing your insights...", minDurationMs: 0 },
  ],

  pipeline: [
    { text: "Thinking...", minDurationMs: 1500 },
    { text: "Understanding your request...", minDurationMs: 1800 },
    { text: "Checking the relevant data...", minDurationMs: 2000 },
    { text: "Preparing your insights...", minDurationMs: 0 },
  ],

  work_order: [
    { text: "Thinking...", minDurationMs: 1500 },
    { text: "Understanding your request...", minDurationMs: 1800 },
    { text: "Checking operational data...", minDurationMs: 2000 },
    { text: "Preparing your insights...", minDurationMs: 0 },
  ],

  cross_board: [
    { text: "Thinking...", minDurationMs: 1500 },
    { text: "Understanding your request...", minDurationMs: 1800 },
    { text: "Checking the relevant data...", minDurationMs: 2000 },
    { text: "Comparing the results...", minDurationMs: 2200 },
    { text: "Preparing your insights...", minDurationMs: 0 },
  ],
};

// ─── Intent Detection ─────────────────────────────────────────────────────────

const GREETING_RE = /^(hi|hello|hey|good morning|good afternoon|good evening|thanks|thank you|sup|howdy)\b/i;
const PIPELINE_RE  = /\b(pipeline|deal|deals|sales|revenue|funnel|opportunity|opportunities|forecast|quota|crm|lead|leads)\b/i;
const WORK_ORDER_RE = /\b(work order|work orders|workorder|project|projects|execution|operational|operations|ops|service|job|jobs|deployment|deployments)\b/i;
const CROSS_BOARD_RE = /\b(compare|comparison|versus|vs\b|against|both|difference|breakdown|split|cross)\b/i;
const BUSINESS_RE = /\b(data|metrics|number|numbers|report|stats|statistics|analytics|performance|kpi|quarter|q[1-4]|monthly|weekly|annual|profit|growth|sector|industry)\b/i;

function detectIntent(message: string): IntentCategory {
  const msg = (message || "").trim();

  if (!msg) return "general";

  // Greeting: only if it's a short conversational opener
  if (GREETING_RE.test(msg) && msg.split(/\s+/).length <= 5) return "greeting";

  // Cross-board before individual categories (it may mention both pipeline + WO)
  if (CROSS_BOARD_RE.test(msg)) return "cross_board";

  if (PIPELINE_RE.test(msg)) return "pipeline";
  if (WORK_ORDER_RE.test(msg)) return "work_order";
  if (BUSINESS_RE.test(msg)) return "business";

  return "general";
}

// ─── Public API ───────────────────────────────────────────────────────────────

/**
 * Returns the ordered one-way stage sequence appropriate for the given message.
 * The caller is responsible for advancing through stages using the
 * `minDurationMs` of each stage as the advancement delay.
 */
export function getLoadingStages(userMessage: string): LoadingStage[] {
  return STAGES[detectIntent(userMessage)];
}
