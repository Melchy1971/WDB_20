/**
 * AiProvider repräsentiert den aktiven KI-Backend-Provider.
 *
 * "none"   — kein Provider konfiguriert (nur serverseitig möglich,
 *             im UI immer genau einer aktiv)
 * "ollama" — lokales Sprachmodell über Ollama
 * "dnabot" — externer DNAbot-Dienst
 */
export type AiProvider = "none" | "ollama" | "dnabot";

/** Subset ohne "none" — für UI-State, der immer einen aktiven Provider erfordert. */
export type ActiveAiProvider = Exclude<AiProvider, "none">;
