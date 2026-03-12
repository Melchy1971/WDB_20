import { useEffect, useRef, useState } from "react";
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

const PICKER_BADGE_LABELS: Record<SourceType, string> = {
  LOCAL_FOLDER: "Ordner gewählt",
  PST: "PST gewählt",
};

export function SourcesPage({ selectedSourceId, onSelectSource, onContinueToScan }: Props) {
  const [sources, setSources] = useState<Source[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [loadError, setLoadError] = useState<string | null>(null);

  const [sourceType, setSourceType] = useState<SourceType>("LOCAL_FOLDER");
  const [label, setLabel] = useState("");
  const [path, setPath] = useState("");
  const [pathLocked, setPathLocked] = useState(false);
  const [pathPickerHint, setPathPickerHint] = useState<string | null>(null);
  const [createState, setCreateState] = useState<CreateState>("idle");
  const [createError, setCreateError] = useState<string | null>(null);
  const folderInputRef = useRef<HTMLInputElement | null>(null);
  const pstInputRef = useRef<HTMLInputElement | null>(null);

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
    setPathLocked(false);
    setPathPickerHint(null);
    setCreateError(null);
  }

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

  function tryExtractFilePath(file: File): string | null {
    const fileWithPath = file as File & { path?: string };
    const absoluteCandidate = fileWithPath.path;
    if (absoluteCandidate && absoluteCandidate.trim()) {
      return absoluteCandidate;
    }
    if (file.name && file.name.trim()) {
      return file.name;
    }
    return null;
  }

  function handlePstFilePicked(event: React.ChangeEvent<HTMLInputElement>): void {
    const files = event.target.files;
    if (!files || files.length === 0) {
      return;
    }

    const pickedFile = files[0];
    const extractedPath = tryExtractFilePath(pickedFile);
    if (!extractedPath) {
      setPathPickerHint(
        "PST-Datei wurde ausgewählt, aber der Browser liefert keinen nutzbaren Pfad. Bitte Pfad manuell eintragen."
      );
      return;
    }

    setPath(extractedPath);
    setPathLocked(true);
    if (extractedPath.includes("/") || extractedPath.includes("\\")) {
      setPathPickerHint(null);
    } else {
      setPathPickerHint(
        "Dateiname übernommen. Falls nötig, ergänzen Sie den vollständigen absoluten Dateipfad zur .pst-Datei."
      );
    }
  }

  function handleOpenPstPicker(): void {
    pstInputRef.current?.click();
  }

  function handleUnlockPath(): void {
    setPathLocked(false);
    setPathPickerHint(null);

    if (sourceType === "LOCAL_FOLDER") {
      handleOpenFolderPicker();
      return;
    }

    if (sourceType === "PST") {
      handleOpenPstPicker();
    }
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
      setPathLocked(false);
      setPathPickerHint(null);
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
          {pathLocked && (
            <span className="picker-selected-badge">{PICKER_BADGE_LABELS[sourceType]}</span>
          )}
        </label>
        {sourceType === "LOCAL_FOLDER" && (
          <>
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
          </>
        )}
        {sourceType === "PST" && (
          <>
            <input
              ref={pstInputRef}
              type="file"
              className="hidden-file-input"
              title="PST-Datei auswählen"
              aria-label="PST-Datei auswählen"
              onChange={handlePstFilePicked}
              accept=".pst"
            />
            <button
              type="button"
              className="action-button action-button--secondary"
              onClick={handleOpenPstPicker}
            >
              PST-Datei auswählen
            </button>
          </>
        )}
        <input
          id="source-path"
          className="text-input"
          type="text"
          value={path}
          onChange={(e) => setPath(e.target.value)}
          placeholder={pathMeta.placeholder}
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
