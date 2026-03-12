import { useEffect, useState } from "react";
import { fetchAiProvider, saveAiProvider } from "../api/aiSettingsApi";
import { StatusBanner } from "../components/status/StatusBanner";
import type { ActiveAiProvider, AiProvider } from "../types/ai";

type LoadState = "loading" | "ready" | "error";
type SaveState = "idle" | "saving" | "success" | "error";

type ProviderConfig = {
  id: ActiveAiProvider;
  label: string;
  description: string;
};

const PROVIDERS: ProviderConfig[] = [
  {
    id: "ollama",
    label: "Local Ollama",
    description: "Lokales Sprachmodell — läuft auf dem eigenen Rechner.",
  },
  {
    id: "dnabot",
    label: "DNAbot",
    description: "Externer DNAbot-Dienst — erfordert Netzwerkverbindung.",
  },
];

export function KiSettingsPage() {
  const [activeProvider, setActiveProvider] = useState<AiProvider>("none");
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchAiProvider()
      .then((provider) => {
        setActiveProvider(provider);
        setLoadState("ready");
      })
      .catch((err: unknown) => {
        setLoadError(err instanceof Error ? err.message : "Fehler beim Laden.");
        setLoadState("error");
      });
  }, []);

  async function handleProviderChange(provider: ActiveAiProvider): Promise<void> {
    setSaveState("saving");
    setSaveMessage(null);
    try {
      const confirmed = await saveAiProvider(provider);
      setActiveProvider(confirmed);
      setSaveState("success");
      setSaveMessage(`Provider gespeichert: ${confirmed}`);
    } catch (err) {
      setSaveState("error");
      setSaveMessage(err instanceof Error ? err.message : "Fehler beim Speichern.");
    }
  }

  return (
    <div className="page">
      <h1>KI-Einstellungen</h1>

      {loadState === "loading" && (
        <p className="status-message pending">Provider wird geladen ...</p>
      )}

      {loadState === "error" && loadError && (
        <StatusBanner message={loadError} variant="error" />
      )}

      {saveMessage && (
        <StatusBanner
          message={saveMessage}
          variant={saveState === "success" ? "success" : "error"}
          onDismiss={() => setSaveMessage(null)}
        />
      )}

      {loadState === "ready" && (
        <div className="panel">
          <h2>Aktiver Provider</h2>
          <p className="hint">Genau ein Provider muss aktiv sein.</p>

          <div className="provider-list">
            {PROVIDERS.map(({ id, label, description }) => {
              const isActive = activeProvider === id;
              const isSaving = saveState === "saving";
              return (
                <div
                  key={id}
                  className={`provider-row${isActive ? " provider-row--active" : ""}`}
                >
                  <div className="provider-info">
                    <span className="provider-label">{label}</span>
                    <span className="provider-description">{description}</span>
                  </div>

                  <button
                    type="button"
                    role="switch"
                    aria-checked={isActive ? "true" : "false"}
                    aria-label={`${label} ${isActive ? "deaktivieren nicht möglich" : "aktivieren"}`}
                    className={`toggle-switch${isActive ? " toggle-switch--on" : ""}`}
                    onClick={() => handleProviderChange(id)}
                    disabled={isActive || isSaving}
                  >
                    <span className="toggle-switch__thumb" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
