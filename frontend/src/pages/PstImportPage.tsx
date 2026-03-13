import { useEffect, useState } from "react";

import { browseFilesystem } from "../api/filesystemApi";
import type { FilesystemBrowseResponse } from "../api/filesystemApi";
import { createPstSource } from "../api/sourcesApi";

type Props = {
  selectedSourceId: string | null;
  selectedSourceType: string | null;
  onOpenPstTree: () => void;
  onImported: (sourceId: string) => Promise<void>;
};

type BrowseState = "idle" | "loading" | "error";

function getFriendlySubmitError(error: unknown): string {
  if (!(error instanceof Error)) {
    return "Fehler beim Einbinden der PST-Datei.";
  }
  if (error.message.includes("Failed to fetch")) {
    return "API nicht erreichbar. Prüfen Sie, ob das Backend läuft.";
  }
  return error.message;
}

export function PstImportPage({
  selectedSourceId,
  selectedSourceType,
  onOpenPstTree,
  onImported,
}: Props) {
  const [label, setLabel] = useState("");
  const [pstPath, setPstPath] = useState("");
  const [submitState, setSubmitState] = useState<"idle" | "saving" | "error">("idle");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [pathError, setPathError] = useState<string | null>(null);

  const [browserOpen, setBrowserOpen] = useState(false);
  const [browseState, setBrowseState] = useState<BrowseState>("idle");
  const [browseError, setBrowseError] = useState<string | null>(null);
  const [browseData, setBrowseData] = useState<FilesystemBrowseResponse | null>(null);

  function navigateTo(path: string | undefined): void {
    setBrowseState("loading");
    setBrowseError(null);
    browseFilesystem(path)
      .then((data) => {
        setBrowseData(data);
        setBrowseState("idle");
      })
      .catch((error: unknown) => {
        const message =
          error instanceof Error ? error.message : "Dateibrowser konnte nicht geladen werden.";
        setBrowseError(
          message.includes("Failed to fetch")
            ? "API nicht erreichbar. Der Dateibrowser konnte nicht geladen werden."
            : message
        );
        setBrowseState("error");
      });
  }

  function openBrowser(): void {
    setBrowserOpen(true);
    if (!browseData) {
      navigateTo(undefined);
    }
  }

  function handleSelectFile(filePath: string): void {
    setPstPath(filePath);
    setPathError(null);
    setSubmitError(null);
    setBrowserOpen(false);
  }

  useEffect(() => {
    if (!browserOpen) {
      setBrowseError(null);
    }
  }, [browserOpen]);

  async function handleSubmit(event: React.FormEvent): Promise<void> {
    event.preventDefault();

    const trimmedLabel = label.trim();
    const trimmedPath = pstPath.trim();

    if (trimmedPath === "") {
      setPathError("Keine Datei gewählt. Wählen Sie eine PST-Datei oder geben Sie einen Netzpfad ein.");
      setSubmitState("error");
      return;
    }

    setPathError(null);
    setSubmitState("saving");
    setSubmitError(null);

    try {
      const source = await createPstSource({ label: trimmedLabel, pst_file_path: trimmedPath });
      await onImported(source.source_id);
    } catch (error) {
      setSubmitState("error");
      setSubmitError(getFriendlySubmitError(error));
    }
  }

  const canSubmit = submitState !== "saving" && label.trim() !== "";

  return (
    <div className="page">
      <h1>PST-Scan & Import</h1>

      {selectedSourceId !== null && selectedSourceType === "PST" && (
        <div className="panel">
          <h2>Aktive PST-Quelle</h2>
          <p className="status-message pending">Aktive Quelle: {selectedSourceId}</p>
          <div className="action-bar">
            <button type="button" className="action-button" onClick={onOpenPstTree}>
              Ordnerstruktur anzeigen
            </button>
          </div>
        </div>
      )}

      <form className="panel" onSubmit={(event) => void handleSubmit(event)}>
        <h2>Neue PST-Datei einbinden</h2>
        <p className="hint">
          Unterstützt lokale Pfade und UNC-Netzpfade wie <code>\\Server\Share\archiv.pst</code>.
        </p>

        <label className="label" htmlFor="pst-label">
          Name
        </label>
        <input
          id="pst-label"
          className="text-input"
          type="text"
          value={label}
          onChange={(event) => setLabel(event.target.value)}
          placeholder="z. B. Postfach Archiv 2023"
          required
        />

        <label className="label" htmlFor="pst-path">
          PST-Dateipfad
        </label>
        <div className="input-with-button">
          <input
            id="pst-path"
            className="text-input"
            type="text"
            value={pstPath}
            onChange={(event) => {
              setPstPath(event.target.value);
              if (pathError !== null) {
                setPathError(null);
              }
            }}
            placeholder={"z. B. C:\\Daten\\archiv.pst oder \\\\Server\\Share\\archiv.pst"}
            required
          />
          <button
            type="button"
            className="action-button action-button--secondary"
            onClick={openBrowser}
          >
            Durchsuchen ...
          </button>
        </div>

        {pathError && <p className="status-message error">{pathError}</p>}

        {browserOpen && (
          <div className="file-browser">
            <div className="file-browser__toolbar">
              <span className="file-browser__current-path">{browseData?.current_path || "Laufwerke"}</span>
              <button
                type="button"
                className="action-button action-button--secondary action-button--small"
                onClick={() => setBrowserOpen(false)}
              >
                Schließen
              </button>
            </div>

            {browseState === "loading" && <p className="status-message pending">Lade ...</p>}
            {browseError && <p className="status-message error">{browseError}</p>}

            {browseState === "idle" && browseData && (
              <ul className="file-browser__list">
                {browseData.parent_path !== null && (
                  <li>
                    <button
                      type="button"
                      className="file-browser__entry file-browser__entry--dir"
                      onClick={() => {
                        const parentPath = browseData.parent_path;
                        navigateTo(parentPath === null || parentPath === "" ? undefined : parentPath);
                      }}
                    >
                      ↑ ..
                    </button>
                  </li>
                )}
                {browseData.entries.length === 0 && (
                  <li>
                    <span className="hint">Keine Ordner oder PST-Dateien gefunden.</span>
                  </li>
                )}
                {browseData.entries.map((entry) => (
                  <li key={entry.path}>
                    {entry.is_dir ? (
                      <button
                        type="button"
                        className="file-browser__entry file-browser__entry--dir"
                        onClick={() => navigateTo(entry.path)}
                      >
                        [DIR] {entry.name}
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="file-browser__entry file-browser__entry--pst"
                        onClick={() => handleSelectFile(entry.path)}
                      >
                        [PST] {entry.name}
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {submitError && <p className="status-message error">{submitError}</p>}

        <button type="submit" className="action-button" disabled={!canSubmit}>
          {submitState === "saving" ? "Einbinden ..." : "PST einbinden und Struktur laden"}
        </button>
      </form>
    </div>
  );
}
