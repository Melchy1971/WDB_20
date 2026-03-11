import { useMemo, useState } from "react";
import { persistDocument } from "../api/persistApi";
import { scanFolder } from "../api/sourcesApi";
import { DocumentList } from "../components/documents/DocumentList";
import { StatusBanner } from "../components/status/StatusBanner";
import type { DocumentScanItem } from "../types/document";
import type { PersistStatus } from "../components/documents/DocumentCard";

type PersistState = {
  status: PersistStatus;
  message: string;
};

type Props = {
  selectedFolderPath: string;
  onFolderPathChange: (path: string) => void;
};

export function FolderScanPage({ selectedFolderPath, onFolderPathChange }: Props) {
  const [documents, setDocuments] = useState<DocumentScanItem[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);
  const [persistStates, setPersistStates] = useState<Record<string, PersistState>>({});

  const scanSummary = useMemo(
    () => (documents.length > 0 ? `${documents.length} Datei(en) gefunden.` : null),
    [documents.length]
  );

  async function handleScan(e: React.FormEvent): Promise<void> {
    e.preventDefault();
    const path = selectedFolderPath.trim();
    setIsScanning(true);
    setScanError(null);
    setPersistStates({});
    try {
      const response = await scanFolder({ folder_path: path });
      setDocuments(response.items);
    } catch (err) {
      setDocuments([]);
      setScanError(err instanceof Error ? err.message : "Unbekannter Fehler beim Scannen.");
    } finally {
      setIsScanning(false);
    }
  }

  async function handlePersist(doc: DocumentScanItem): Promise<void> {
    setPersistStates((prev) => ({
      ...prev,
      [doc.file_path]: { status: "saving", message: "Speicherung läuft ..." },
    }));
    try {
      const response = await persistDocument(doc.content_hash);
      setPersistStates((prev) => ({
        ...prev,
        [doc.file_path]: {
          status: "success",
          message: `Erfolgreich gespeichert: ${response.file_path}`,
        },
      }));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unbekannter Fehler beim Speichern.";
      setPersistStates((prev) => ({
        ...prev,
        [doc.file_path]: { status: "error", message },
      }));
    }
  }

  return (
    <div className="page">
      <h1>Dokumentenimport</h1>

      <form className="panel" onSubmit={handleScan}>
        <h2>Lokalen Ordner scannen</h2>
        <label className="label" htmlFor="folder-path">
          Ordnerpfad
        </label>
        <input
          id="folder-path"
          className="text-input"
          type="text"
          value={selectedFolderPath}
          onChange={(e) => onFolderPathChange(e.target.value)}
          placeholder="z. B. /workspace/data/sample_docs"
          required
        />
        <button
          className="action-button"
          type="submit"
          disabled={isScanning || selectedFolderPath.trim().length === 0}
        >
          {isScanning ? "Scanne ..." : "Ordner scannen"}
        </button>
      </form>

      {scanError && (
        <StatusBanner message={scanError} variant="error" onDismiss={() => setScanError(null)} />
      )}
      {scanSummary && <StatusBanner message={scanSummary} variant="success" />}

      <DocumentList
        documents={documents}
        persistStates={persistStates}
        onPersist={handlePersist}
        isScanning={isScanning}
      />
    </div>
  );
}
