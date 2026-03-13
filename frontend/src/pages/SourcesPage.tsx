import { useEffect, useRef, useState } from "react";
import {
  createSource,
  deleteSource,
  listSources,
  updateSourcePath,
} from "../api/sourcesApi";
import { StatusBanner } from "../components/status/StatusBanner";
import type { Source } from "../types/source";

type LoadState = "loading" | "ready" | "error";
type CreateState = "idle" | "saving" | "error";
type EditState = "idle" | "saving" | "error";

type Props = {
  selectedSourceId: string | null;
  onSelectSource: (sourceId: string, sourceType: string) => Promise<void>;
  onContinueToScan: () => void;
};


export function SourcesPage({ selectedSourceId, onSelectSource, onContinueToScan }: Props) {
  const [sources, setSources] = useState<Source[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [loadError, setLoadError] = useState<string | null>(null);

  const [label, setLabel] = useState("");
  const [path, setPath] = useState("");
  const [pathLocked, setPathLocked] = useState(false);
  const [pathPickerHint, setPathPickerHint] = useState<string | null>(null);
  const [createState, setCreateState] = useState<CreateState>("idle");
  const [createError, setCreateError] = useState<string | null>(null);

  const [editingSourceId, setEditingSourceId] = useState<string | null>(null);
  const [editingPath, setEditingPath] = useState("");
  const [editState, setEditState] = useState<EditState>("idle");
  const [editError, setEditError] = useState<string | null>(null);

  const folderInputRef = useRef<HTMLInputElement | null>(null);

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

  function tryExtractFolderPathFromFile(file: File): string | null {
    const fileWithPath = file as File & { path?: string; webkitRelativePath?: string };
    const absoluteCandidate = fileWithPath.path;
    if (absoluteCandidate && absoluteCandidate.trim()) {
      const normalized = absoluteCandidate.replace(/\\/g, "/");
      const lastSlash = normalized.lastIndexOf("/");
      if (lastSlash > 0) {
        return normalized.slice(0, lastSlash);
      }
    }

    const relativeCandidate = fileWithPath.webkitRelativePath;
    if (relativeCandidate && relativeCandidate.trim()) {
      const topFolder = relativeCandidate.split("/")[0];
      if (topFolder) {
        return topFolder;
      }
    }

    return null;
  }

  function handleFolderPicked(event: React.ChangeEvent<HTMLInputElement>): void {
    const files = event.target.files;
    if (!files || files.length === 0) {
      return;
    }

    const extractedPath = tryExtractFolderPathFromFile(files[0]);
    if (!extractedPath) {
      setPathPickerHint(
        "Ordner wurde ausgewählt, aber der Browser liefert keinen nutzbaren Pfad. Bitte Pfad manuell eintragen."
      );
      return;
    }

    setPath(extractedPath);
    setPathLocked(true);
    if (extractedPath.includes("/") || extractedPath.includes("\\")) {
      setPathPickerHint(null);
    } else {
      setPathPickerHint(
        "Ordnername übernommen. Falls nötig, ergänzen Sie den vollständigen absoluten Ordnerpfad."
      );
    }
  }

  function handleOpenFolderPicker(): void {
    folderInputRef.current?.click();
  }

  function handleUnlockPath(): void {
    setPathLocked(false);
    setPathPickerHint(null);
    handleOpenFolderPicker();
  }

  function startEditing(source: Source): void {
    setEditingSourceId(source.source_id);
    setEditingPath(source.source_path);
    setEditState("idle");
    setEditError(null);
    setCreateError(null);
  }

  function cancelEditing(): void {
    setEditingSourceId(null);
    setEditingPath("");
    setEditState("idle");
    setEditError(null);
  }

  async function handleSaveSourcePath(source: Source): Promise<void> {
    const trimmedPath = editingPath.trim();
    if (!trimmedPath) {
      setEditState("error");
      setEditError("Pfad darf nicht leer sein.");
      return;
    }

    setEditState("saving");
    setEditError(null);
    try {
      const updated = await updateSourcePath(source.source_id, { source_path: trimmedPath });
      setSources((prev) => prev.map((entry) => (entry.source_id === updated.source_id ? updated : entry)));
      cancelEditing();
    } catch (err) {
      setEditState("error");
      setEditError(err instanceof Error ? err.message : "Pfad konnte nicht gespeichert werden.");
    }
  }

  async function handleCreate(e: React.FormEvent): Promise<void> {
    e.preventDefault();

    setCreateState("saving");
    setCreateError(null);
    try {
      const newSource = await createSource({
        source_type: "LOCAL_FOLDER",
        label: label.trim(),
        source_path: path.trim(),
      });
      setSources((prev) => [...prev, newSource]);
      setLabel("");
      setPath("");
      setPathLocked(false);
      setPathPickerHint(null);
      setCreateState("idle");
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : "Fehler beim Anlegen der Quelle.");
      setCreateState("error");
    }
  }

  return (
    <div className="page">
      <h1>Quellenverwaltung</h1>

      <form className="panel" onSubmit={handleCreate}>
        <h2>Neue Quelle anlegen</h2>

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
          Ordnerpfad
          {pathLocked && <span className="picker-selected-badge">Ordner gewählt</span>}
        </label>
        <input
          ref={folderInputRef}
          type="file"
          className="hidden-file-input"
          title="Lokalen Ordner auswählen"
          aria-label="Lokalen Ordner auswählen"
          onChange={handleFolderPicked}
          multiple
          {...({ webkitdirectory: "", directory: "" } as Record<string, string>)}
        />
        <button
          type="button"
          className="action-button action-button--secondary"
          onClick={handleOpenFolderPicker}
        >
          Lokalen Ordner auswählen
        </button>
        <input
          id="source-path"
          className="text-input"
          type="text"
          value={path}
          onChange={(e) => setPath(e.target.value)}
          placeholder="z. B. /workspace/data/sample_docs"
          readOnly={pathLocked}
          required
        />

        {pathLocked && (
          <div className="action-bar">
            <button
              type="button"
              className="action-button action-button--secondary"
              onClick={handleUnlockPath}
            >
              Ändern (neu auswählen)
            </button>
          </div>
        )}

        {pathPickerHint && <p className="hint">{pathPickerHint}</p>}
        {createError && <p className="status-message error">{createError}</p>}
        <button
          type="submit"
          className="action-button"
          disabled={createState === "saving" || !label.trim() || !path.trim()}
        >
          {createState === "saving" ? "Speichern ..." : "Quelle anlegen"}
        </button>
      </form>

      {loadState === "loading" && <p className="status-message pending">Quellen werden geladen ...</p>}
      {loadState === "error" && loadError && <StatusBanner message={loadError} variant="error" />}

      {loadState === "ready" && (
        <div className="panel">
          <h2>Registrierte Quellen</h2>
          {sources.length === 0 ? (
            <p className="hint">Noch keine Quellen vorhanden. Legen Sie oben eine neue Quelle an.</p>
          ) : (
            <div className="source-list">
              {sources.map((source) => {
                const isActive = selectedSourceId === source.source_id;
                const isEditing = editingSourceId === source.source_id;
                const primaryButtonLabel = isActive ? "Zum Scan" : "Aktivieren + Scan";

                return (
                  <div
                    key={source.source_id}
                    className={`source-item${isActive ? " source-item--active" : ""}`}
                  >
                    <div className="source-item__info">
                      <div className="source-item__header">
                        <span className="source-item__label">{source.label}</span>
                      </div>

                      {isEditing ? (
                        <>
                          <input
                            className="text-input source-item__path-input"
                            type="text"
                            value={editingPath}
                            onChange={(e) => setEditingPath(e.target.value)}
                            placeholder="z. B. /workspace/data/sample_docs"
                          />
                          {editError && <p className="status-message error">{editError}</p>}
                        </>
                      ) : (
                        <span className="source-item__path">{source.source_path}</span>
                      )}

                      <span className="source-item__type">Lokaler Ordner</span>
                    </div>

                    <div className="source-item__actions">
                      {isEditing ? (
                        <>
                          <button
                            type="button"
                            className="action-button"
                            onClick={() => void handleSaveSourcePath(source)}
                            disabled={editState === "saving"}
                          >
                            {editState === "saving" ? "Speichern ..." : "Pfad speichern"}
                          </button>
                          <button
                            type="button"
                            className="action-button action-button--secondary"
                            onClick={cancelEditing}
                            disabled={editState === "saving"}
                          >
                            Abbrechen
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            type="button"
                            className="action-button action-button--secondary"
                            onClick={async () => {
                              try {
                                await onSelectSource(source.source_id, source.source_type);
                              } catch (err) {
                                setCreateError(err instanceof Error ? err.message : "Quelle konnte nicht aktiviert werden.");
                              }
                            }}
                            disabled={isActive}
                          >
                            {isActive ? "Aktiv" : "Aktivieren"}
                          </button>
                          <button
                            type="button"
                            className="action-button"
                            onClick={async () => {
                              try {
                                await onSelectSource(source.source_id, source.source_type);
                                onContinueToScan();
                              } catch (err) {
                                setCreateError(err instanceof Error ? err.message : "Quelle konnte nicht aktiviert werden.");
                              }
                            }}
                          >
                            {primaryButtonLabel}
                          </button>
                          <button
                            type="button"
                            className="action-button action-button--secondary"
                            onClick={() => startEditing(source)}
                          >
                            Bearbeiten
                          </button>
                          <button
                            type="button"
                            className="action-button action-button--danger"
                            onClick={async () => {
                              try {
                                await deleteSource(source.source_id);
                                setSources((prev) => prev.filter((s) => s.source_id !== source.source_id));
                                if (editingSourceId === source.source_id) {
                                  cancelEditing();
                                }
                              } catch {
                                alert("Quelle konnte nicht entfernt werden.");
                              }
                            }}
                          >
                            Entfernen
                          </button>
                        </>
                      )}
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
