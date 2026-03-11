import { useMemo, useState } from "react";
import { persistDocument } from "../api/persistApi";
import { scanFolder } from "../api/sourcesApi";
import type { DocumentItem } from "../types/document";

type PersistState = {
  status: "idle" | "saving" | "success" | "error";
  message: string;
};

export function FolderScanPage() {
  const [folderPath, setFolderPath] = useState("");
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);
  const [persistStates, setPersistStates] = useState<Record<string, PersistState>>({});

  const hasDocuments = documents.length > 0;

  const scanSummary = useMemo(() => {
    if (!hasDocuments) {
      return "Noch keine Dateien geladen.";
    }

<<<<<<< HEAD
    return `${documents.length} Textdatei(en) gefunden.`;
  }, [documents.length, hasDocuments]);

  async function handleScanFolder(): Promise<void> {
    setIsScanning(true);
    setScanError(null);
    setPersistStates({});

    try {
      const response = await scanFolder({ folder_path: folderPath.trim() });
      setDocuments(response.items);
    } catch (error) {
      setDocuments([]);
      setScanError(error instanceof Error ? error.message : "Unbekannter Fehler beim Scannen.");
    } finally {
      setIsScanning(false);
    }
  }
=======
	async function handlePersist(item: DocumentItem) {
		try {
			setPersistMessage("");
			setError("");
			const result = await persistDocument(item);
			setPersistMessage(`Gespeichert: ${result.file_path}`);
		} catch (err) {
			setError(err instanceof Error ? err.message : "Persistenzfehler");
		}
	}

	return (
		<div className="page">
			<h1>Dokumentscan</h1>

			<div className="card">
				<h2>Lokaler Ordnerpfad</h2>
				<input
					type="text"
					value={folderPath}
					onChange={(e) => setFolderPath(e.target.value)}
					placeholder="C:\\mail-knowledge-platform\\data\\sample_docs"
					className="text-input"
				/>
				<button onClick={handleScan} disabled={loading || !folderPath} className="action-button">
					{loading ? "Scanne ..." : "Ordner scannen"}
				</button>
			</div>
>>>>>>> a19e3da ( Changes to be committed:)

  async function handlePersistDocument(document: DocumentItem): Promise<void> {
    setPersistStates((previous) => ({
      ...previous,
      [document.file_path]: {
        status: "saving",
        message: "Speicherung läuft ...",
      },
    }));

<<<<<<< HEAD
    try {
      const response = await persistDocument(document);

      setPersistStates((previous) => ({
        ...previous,
        [document.file_path]: {
          status: "success",
          message: `Erfolgreich gespeichert: ${response.file_path}`,
        },
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unbekannter Fehler beim Speichern.";

      setPersistStates((previous) => ({
        ...previous,
        [document.file_path]: {
          status: "error",
          message,
        },
      }));
    }
  }

  return (
    <main className="page">
      <h1>Dokumentenimport (Vertical Slice)</h1>

      <section className="panel">
        <h2>1) Lokalen Ordner scannen</h2>
        <label htmlFor="folder-path" className="label">
          Ordnerpfad
        </label>
        <input
          id="folder-path"
          className="text-input"
          type="text"
          value={folderPath}
          onChange={(event) => setFolderPath(event.target.value)}
          placeholder="z. B. /workspace/WDB_20/mail-knowledge-platform/data/sample_docs"
        />
        <button
          className="action-button"
          type="button"
          onClick={handleScanFolder}
          disabled={isScanning || folderPath.trim().length === 0}
        >
          {isScanning ? "Scanne Ordner ..." : "Ordner scannen"}
        </button>

        <p className="hint">{scanSummary}</p>
        {scanError && <p className="status-message error">{scanError}</p>}
      </section>

      <section>
        <h2>2) Gefundene .txt-Dateien</h2>
        {!hasDocuments && !isScanning && <p className="hint">Keine Dateien zur Anzeige.</p>}

        <div className="card-grid">
          {documents.map((document) => {
            const persistState = persistStates[document.file_path];
            const isSaving = persistState?.status === "saving";

            return (
              <article className="card" key={document.file_path}>
                <h3>{document.file_name}</h3>
                <p>
                  <strong>Pfad:</strong> {document.file_path}
                </p>
                <p>
                  <strong>Größe:</strong> {document.size_bytes} Bytes
                </p>
                <p>
                  <strong>Letzte Änderung:</strong> {document.last_modified}
                </p>

                <button
                  className="action-button"
                  type="button"
                  onClick={() => handlePersistDocument(document)}
                  disabled={isSaving}
                >
                  {isSaving ? "Speichere ..." : "In Neo4j speichern"}
                </button>

                {persistState && (
                  <p
                    className={`status-message ${
                      persistState.status === "success"
                        ? "success"
                        : persistState.status === "error"
                          ? "error"
                          : "pending"
                    }`}
                  >
                    {persistState.message}
                  </p>
                )}
              </article>
            );
          })}
        </div>
      </section>
    </main>
  );
=======
			<div className="card-grid">
				{items.map((item) => (
					<div className="card" key={item.file_path}>
						<h2>{item.file_name}</h2>
						<p><strong>Typ:</strong> {item.extension}</p>
						<p><strong>MIME:</strong> {item.mime_type}</p>
						<p><strong>Parser:</strong> {item.parser_type}</p>
						<p><strong>Status:</strong> {item.parse_status}</p>
						<p><strong>Pfad:</strong> {item.file_path}</p>
						<p><strong>Groesse:</strong> {item.size_bytes} Bytes</p>
						<p><strong>Geaendert:</strong> {item.last_modified}</p>
						<p><strong>Preview:</strong></p>
						<div className="preview-box">{item.preview_text || "[leer]"}</div>
						<button onClick={() => handlePersist(item)} className="action-button">
							In Neo4j speichern
						</button>
					</div>
				))}
			</div>
		</div>
	);
>>>>>>> a19e3da ( Changes to be committed:)
}
