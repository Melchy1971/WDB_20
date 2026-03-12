import { useEffect, useState } from "react";
import { createPstSource, createSource, listSources } from "../api/sourcesApi";
import { StatusBanner } from "../components/status/StatusBanner";
import type { Source, SourceType } from "../types/source";

type LoadState = "loading" | "ready" | "error";
type CreateState = "idle" | "saving" | "error";

type Props = {
  selectedSourceId: string | null;
  onSelectSource: (sourceId: string) => void;
  onContinueToScan: () => void;
};

const SOURCE_TYPE_LABELS: Record<SourceType, string> = {
  LOCAL_FOLDER: "Lokaler Ordner",
  PST: "PST-Datei",
};

const PATH_LABELS: Record<SourceType, { label: string; placeholder: string }> = {
  LOCAL_FOLDER: {
    label: "Ordnerpfad",
    placeholder: "z. B. /workspace/data/sample_docs",
  },
  PST: {
    label: "PST-Dateipfad",
    placeholder: "z. B. /data/archive/postfach.pst",
  },
};

export function SourcesPage({ selectedSourceId, onSelectSource, onContinueToScan }: Props) {
  const [sources, setSources] = useState<Source[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [loadError, setLoadError] = useState<string | null>(null);

  const [sourceType, setSourceType] = useState<SourceType>("LOCAL_FOLDER");
  const [label, setLabel] = useState("");
  const [path, setPath] = useState("");
  const [createState, setCreateState] = useState<CreateState>("idle");
  const [createError, setCreateError] = useState<string | null>(null);

  useEffect(() => {
    listSources()
      .then((data) => {
        setSources(data);
        setLoadState("ready");
      })
      .catch((err: unknown) => {
        setLoadError(err instanceof Error ? err.message : "Fehler beim Laden der Quellen.");
        setLoadState("error");
      });
  }, []);

  function handleTypeChange(newType: SourceType): void {
    setSourceType(newType);
    setPath("");
    setCreateError(null);
  }

  async function handleCreate(e: React.FormEvent): Promise<void> {
    e.preventDefault();
    setCreateState("saving");
    setCreateError(null);
    try {
      let newSource: Source;
      if (sourceType === "PST") {
        newSource = await createPstSource({ label: label.trim(), pst_file_path: path.trim() });
      } else {
        newSource = await createSource({
          source_type: "LOCAL_FOLDER",
          label: label.trim(),
          source_path: path.trim(),
        });
      }
      setSources((prev) => [...prev, newSource]);
      setLabel("");
      setPath("");
      setCreateState("idle");
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : "Fehler beim Anlegen der Quelle.");
      setCreateState("error");
    }
  }

  const pathMeta = PATH_LABELS[sourceType];

  return (
    <div className="page">
      <h1>Quellenverwaltung</h1>

      <form className="panel" onSubmit={handleCreate}>
        <h2>Neue Quelle anlegen</h2>

        <label className="label" htmlFor="source-type">
          Quellentyp
        </label>
        <select
          id="source-type"
          className="text-input"
          value={sourceType}
          onChange={(e) => handleTypeChange(e.target.value as SourceType)}
        >
          {(Object.keys(SOURCE_TYPE_LABELS) as SourceType[]).map((type) => (
            <option key={type} value={type}>
              {SOURCE_TYPE_LABELS[type]}
            </option>
          ))}
        </select>

        <label className="label" htmlFor="source-label">
          Name
        </label>
        <input
          id="source-label"
          className="text-input"
          type="text"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          placeholder="z. B. Projektdokumente 2024"
          required
        />

        <label className="label" htmlFor="source-path">
          {pathMeta.label}
        </label>
        <input
          id="source-path"
          className="text-input"
          type="text"
          value={path}
          onChange={(e) => setPath(e.target.value)}
          placeholder={pathMeta.placeholder}
          required
        />

        {createError && (
          <p className="status-message error">{createError}</p>
        )}
        <button
          type="submit"
          className="action-button"
          disabled={createState === "saving" || !label.trim() || !path.trim()}
        >
          {createState === "saving" ? "Speichern ..." : "Quelle anlegen"}
        </button>
      </form>

      {loadState === "loading" && (
        <p className="status-message pending">Quellen werden geladen ...</p>
      )}

      {loadState === "error" && loadError && (
        <StatusBanner message={loadError} variant="error" />
      )}

      {loadState === "ready" && (
        <div className="panel">
          <h2>Registrierte Quellen</h2>
          {sources.length === 0 ? (
            <p className="hint">Noch keine Quellen vorhanden. Legen Sie oben eine neue Quelle an.</p>
          ) : (
            <div className="source-list">
              {sources.map((source) => {
                const isActive = selectedSourceId === source.source_id;
                return (
                  <div
                    key={source.source_id}
                    className={`source-item${isActive ? " source-item--active" : ""}`}
                  >
                    <div className="source-item__info">
                      <span className="source-item__label">{source.label}</span>
                      <span className="source-item__path">{source.source_path}</span>
                      <span className="source-item__type">
                        {SOURCE_TYPE_LABELS[source.source_type]}
                      </span>
                    </div>
                    <div className="source-item__actions">
                      <button
                        type="button"
                        className="action-button action-button--secondary"
                        onClick={() => onSelectSource(source.source_id)}
                        disabled={isActive}
                      >
                        {isActive ? "Aktiv" : "Aktivieren"}
                      </button>
                      <button
                        type="button"
                        className="action-button"
                        onClick={() => {
                          onSelectSource(source.source_id);
                          onContinueToScan();
                        }}
                      >
                        {isActive ? "Zum Scan" : "Aktivieren + Scan"}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
