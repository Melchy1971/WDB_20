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

export function PstImportPage({ selectedSourceId, selectedSourceType, onOpenPstTree, onImported }: Props) {
  const [label, setLabel] = useState("");
  const [pstPath, setPstPath] = useState("");
  const [submitState, setSubmitState] = useState<"idle" | "saving" | "error">("idle");
  const [submitError, setSubmitError] = useState<string | null>(null);

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
      .catch((err: unknown) => {
        setBrowseError(err instanceof Error ? err.message : "Fehler beim Laden.");
        setBrowseState("idle");
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
    setBrowserOpen(false);
  }

  // Reset browser when closed
  useEffect(() => {
    if (!browserOpen) {
      setBrowseError(null);
    }
  }, [browserOpen]);

  async function handleSubmit(e: React.FormEvent): Promise<void> {
    e.preventDefault();
    setSubmitState("saving");
    setSubmitError(null);
    try {
      const source = await createPstSource({ label: label.trim(), pst_file_path: pstPath.trim() });
      await onImported(source.source_id);
    } catch (err) {
      setSubmitState("error");
      setSubmitError(err instanceof Error ? err.message : "Fehler beim Einbinden der PST-Datei.");
    }
  }

  const canSubmit = submitState !== "saving" && label.trim() !== "" && pstPath.trim() !== "";

  return (
    <div className="page">
      <h1>PST-Scan & Import</h1>

      {selectedSourceId !== null && selectedSourceType === "PST" && (
        <div className="panel">
          <h2>PST scannen</h2>
          <p className="status-message pending">Aktive Quelle: {selectedSourceId}</p>
          <p className="hint">PST-Dateien werden hier separat gescannt. Der Scan liest die PST-Struktur fuer Auswahl und Import vor.</p>
          <div className="action-bar">
            <button
              type="button"
              className="action-button"
              onClick={onOpenPstTree}
            >
              PST scannen
            </button>
          </div>
        </div>
      )}

      <form className="panel" onSubmit={(e) => void handleSubmit(e)}>
        <h2>Neue PST-Datei einbinden</h2>

        <label className="label" htmlFor="pst-label">
          Name
        </label>
        <input
          id="pst-label"
          className="text-input"
          type="text"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
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
            onChange={(e) => setPstPath(e.target.value)}
            placeholder={`z. B. C:\\Daten\\archiv.pst  oder  \\\\Server\\Share\\archiv.pst`}
            required
          />
          <button
            type="button"
            className="action-button action-button--secondary"
            onClick={openBrowser}
          >
            Durchsuchen …
          </button>
        </div>

        {browserOpen && (
          <div className="file-browser">
            <div className="file-browser__toolbar">
              <span className="file-browser__current-path">
                {browseData?.current_path || "Laufwerke"}
              </span>
              <button
                type="button"
                className="action-button action-button--secondary action-button--small"
                onClick={() => setBrowserOpen(false)}
              >
                Schließen
              </button>
            </div>

            {browseState === "loading" && (
              <p className="status-message pending">Lade ...</p>
            )}

            {browseError && (
              <p className="status-message error">{browseError}</p>
            )}

            {browseState === "idle" && browseData && (
              <ul className="file-browser__list">
                {browseData.parent_path !== null && (
                  <li>
                    <button
                      type="button"
                      className="file-browser__entry file-browser__entry--dir"
                      onClick={() => navigateTo(browseData.parent_path === "" ? undefined : browseData.parent_path)}
                    >
                      ↑ ..
                    </button>
                  </li>
                )}
                {browseData.entries.length === 0 && (
                  <li><span className="hint">Keine Ordner oder PST-Dateien gefunden.</span></li>
                )}
                {browseData.entries.map((entry) => (
                  <li key={entry.path}>
                    {entry.is_dir ? (
                      <button
                        type="button"
                        className="file-browser__entry file-browser__entry--dir"
                        onClick={() => navigateTo(entry.path)}
                      >
                        📁 {entry.name}
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="file-browser__entry file-browser__entry--pst"
                        onClick={() => handleSelectFile(entry.path)}
                      >
                        📄 {entry.name}
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {submitError && <p className="status-message error">{submitError}</p>}

        <button
          type="submit"
          className="action-button"
          disabled={!canSubmit}
        >
          {submitState === "saving" ? "Einbinden ..." : "PST einbinden"}
        </button>
      </form>
    </div>
  );
}
