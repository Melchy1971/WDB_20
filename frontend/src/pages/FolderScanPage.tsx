import { useMemo, useState } from "react";
import { persistDocument } from "../api/persistApi";
import { scanSource } from "../api/sourcesApi";
import { DocumentList } from "../components/documents/DocumentList";
import { StatusBanner } from "../components/status/StatusBanner";
import type { DocumentScanItem } from "../types/document";
import type { PersistStatus } from "../components/documents/DocumentCard";

type PersistState = {
  status: PersistStatus;
  message: string;
};

type Props = {
  selectedSourceId: string | null;
};

export function FolderScanPage({ selectedSourceId }: Props) {
  const [documents, setDocuments] = useState<DocumentScanItem[]>([]);
  const [scanId, setScanId] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);
  const [persistStates, setPersistStates] = useState<Record<string, PersistState>>({});

  const scanSummary = useMemo(
    () => (documents.length > 0 ? `${documents.length} Datei(en) gefunden.` : null),
    [documents.length]
  );

  async function handleScan(e: React.FormEvent): Promise<void> {
    e.preventDefault();
    if (selectedSourceId === null) return;
    setIsScanning(true);
    setScanError(null);
    setScanId(null);
    setPersistStates({});
    try {
      const response = await scanSource(selectedSourceId);
      setScanId(response.scan_id);
      setDocuments(response.items);
    } catch (err) {
      setDocuments([]);
      setScanError(err instanceof Error ? err.message : "Unbekannter Fehler beim Scannen.");
    } finally {
      setIsScanning(false);
    }
  }

  async function handlePersist(doc: DocumentScanItem): Promise<void> {
    if (scanId === null) return;
    setPersistStates((prev) => ({
      ...prev,
      [doc.document_id]: { status: "saving", message: "Speicherung läuft ..." },
    }));
    try {
      const response = await persistDocument(scanId, doc.document_id);
      setPersistStates((prev) => ({
        ...prev,
        [doc.document_id]: {
          status: "success",
          message: `Erfolgreich gespeichert: ${response.file_path}`,
        },
      }));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unbekannter Fehler beim Speichern.";
      setPersistStates((prev) => ({
        ...prev,
        [doc.document_id]: { status: "error", message },
      }));
    }
  }

  return (
    <div className="page">
      <h1>Dokumentenimport</h1>

      <form className="panel" onSubmit={handleScan}>
        <h2>Quelle scannen</h2>
        {selectedSourceId === null ? (
          <p className="hint">Keine Quelle aktiv. Wählen Sie zuerst eine Quelle in der Quellenverwaltung.</p>
        ) : (
          <p className="status-message pending">Aktive Quelle: {selectedSourceId}</p>
        )}
        <button
          className="action-button"
          type="submit"
          disabled={isScanning || selectedSourceId === null}
        >
          {isScanning ? "Scanne ..." : "Quelle scannen"}
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
