/**
 * AiProvider repräsentiert den aktiven KI-Backend-Provider.
 *
 * "none"   — kein Provider konfiguriert (Backend-Default nach Start)
 * "ollama" — lokales Sprachmodell über Ollama
 * "dnabot" — externer DNAbot-Dienst
 */
export type AiProvider = "none" | "ollama" | "dnabot";

/**
 * ActiveAiProvider — wählbare Provider im UI.
 * "none" ist kein wählbarer Zustand: er tritt nur als Backend-Default auf,
 * nicht als Ergebnis einer Nutzerauswahl.
 */
export type ActiveAiProvider = Exclude<AiProvider, "none">;

/** GET /settings/ai-provider */
export type AiProviderGetResponse = {
  active_provider: AiProvider;
};

/**
 * POST /settings/ai-provider — Request-Body.
 * Nur ActiveAiProvider: die UI schickt nie "none".
 */
export type AiProviderSetRequest = {
  active_provider: ActiveAiProvider;
};

/** POST /settings/ai-provider — Response */
export type AiProviderSetResponse = {
  status: "updated";
  active_provider: AiProvider;
};
