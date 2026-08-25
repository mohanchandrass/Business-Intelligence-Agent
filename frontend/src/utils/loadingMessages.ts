/**
 * Lightweight deterministic loading message utility.
 * Uses keyword matching to pick appropriate message sets — no LLM calls.
 */

type MessageSet = readonly string[];

const GREETING_MESSAGES: MessageSet = [
  "Thinking...",
  "Preparing a response...",
  "Getting back to you...",
];

const PIPELINE_MESSAGES: MessageSet = [
  "Checking the pipeline...",
  "Reviewing deal data...",
  "Working through the pipeline...",
  "Preparing your insights...",
];

const WORK_ORDER_MESSAGES: MessageSet = [
  "Reviewing work orders...",
  "Checking operational data...",
  "Looking for relevant work orders...",
  "Working through the numbers...",
];

const CROSS_BOARD_MESSAGES: MessageSet = [
  "Comparing business data...",
  "Connecting the relevant data...",
  "Working across your data...",
  "Preparing the comparison...",
];

const BUSINESS_MESSAGES: MessageSet = [
  "Looking through the business data...",
  "Checking the relevant data...",
  "Working through the numbers...",
  "Preparing your insights...",
];

const GENERAL_MESSAGES: MessageSet = [
  "Thinking...",
  "Working on that...",
  "Preparing your answer...",
  "Looking into it...",
];

// Keyword sets
const GREETING_KEYWORDS = /^(hi|hello|hey|good morning|good afternoon|good evening|thanks|thank you|sup|howdy)\b/i;

const PIPELINE_KEYWORDS = /\b(pipeline|deal|deals|sales|revenue|funnel|opportunity|opportunities|forecast|quota|crm|lead|leads)\b/i;

const WORK_ORDER_KEYWORDS = /\b(work order|work orders|workorder|project|projects|execution|operational|operations|ops|service|job|jobs|deployment|deployments)\b/i;

const CROSS_BOARD_KEYWORDS = /\b(compare|comparison|versus|vs\b|against|both|difference|breakdown|split|cross)\b/i;

const BUSINESS_KEYWORDS = /\b(data|metrics|number|numbers|report|stats|statistics|analytics|performance|kpi|quarter|q1|q2|q3|q4|monthly|weekly|annual|revenue|profit|growth|sector|industry)\b/i;

export function getLoadingMessages(userMessage: string): MessageSet {
  const msg = (userMessage || "").trim();

  if (!msg) return GENERAL_MESSAGES;

  // Greeting check first — short-circuit before any data analysis wording
  if (GREETING_KEYWORDS.test(msg) && msg.split(/\s+/).length <= 5) {
    return GREETING_MESSAGES;
  }

  // Cross-board / comparison — check before individual board categories
  if (CROSS_BOARD_KEYWORDS.test(msg)) {
    return CROSS_BOARD_MESSAGES;
  }

  // Pipeline / deals
  if (PIPELINE_KEYWORDS.test(msg)) {
    return PIPELINE_MESSAGES;
  }

  // Work orders / operations
  if (WORK_ORDER_KEYWORDS.test(msg)) {
    return WORK_ORDER_MESSAGES;
  }

  // General business / data questions
  if (BUSINESS_KEYWORDS.test(msg)) {
    return BUSINESS_MESSAGES;
  }

  return GENERAL_MESSAGES;
}
