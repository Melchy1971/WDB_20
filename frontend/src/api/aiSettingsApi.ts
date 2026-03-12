import { apiGet, apiPost } from "./client";
import type {
  ActiveAiProvider,
  AiProvider,
  AiProviderGetResponse,
  AiProviderSetRequest,
  AiProviderSetResponse,
} from "../types/ai";

export function fetchAiProvider(): Promise<AiProvider> {
  return apiGet<AiProviderGetResponse>("/settings/ai-provider").then(
    (res) => res.active_provider
  );
}

/**
 * Sendet einen Providerwechsel an das Backend und gibt den vom Backend
 * bestätigten Wert zurück — nie einen lokalen Annahmewert.
 */
export function saveAiProvider(provider: ActiveAiProvider): Promise<AiProvider> {
  return apiPost<AiProviderSetRequest, AiProviderSetResponse>(
    "/settings/ai-provider",
    { active_provider: provider }
  ).then((res) => res.active_provider);
}
