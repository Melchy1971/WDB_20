import type { ActiveAiProvider } from "../types/ai";

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

type Props = {
  activeProvider: ActiveAiProvider;
  onProviderChange: (provider: ActiveAiProvider) => void;
};

export function KiSettingsPage({ activeProvider, onProviderChange }: Props) {
  return (
    <div className="page">
      <h1>KI-Einstellungen</h1>

      <div className="panel">
        <h2>Aktiver Provider</h2>
        <p className="hint">Genau ein Provider muss aktiv sein.</p>

        <div className="provider-list">
          {PROVIDERS.map(({ id, label, description }) => {
            const isActive = activeProvider === id;
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
                  aria-checked={isActive}
                  aria-label={`${label} ${isActive ? "deaktivieren nicht möglich" : "aktivieren"}`}
                  className={`toggle-switch${isActive ? " toggle-switch--on" : ""}`}
                  onClick={() => onProviderChange(id)}
                  disabled={isActive}
                >
                  <span className="toggle-switch__thumb" />
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
