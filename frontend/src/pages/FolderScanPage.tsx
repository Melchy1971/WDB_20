import { useMemo, useState } from "react";
import { persistDocument } from "../api/persistApi";
import { scanFolder } from "../api/sourcesApi";
import { DocumentList } from "../components/documents/DocumentList";
import { FolderScanForm } from "../components/sources/FolderScanForm";
import { StatusBanner } from "../components/status/StatusBanner";
import type { DocumentScanItem } from "../types/document";
import type { PersistStatus } from "../components/documents/DocumentCard";

type PersistState = {
  status: PersistStatus;
  message: string;
};

export function FolderScanPage() {
  const [documents, setDocuments] = useState<DocumentScanItem[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);
  const [persistStates, setPersistStates] = useState<Record<string, PersistState>>({});

  const scanSummary = useMemo(
    () => (documents.length > 0 ? `${documents.length} Datei(en) gefunden.` : null),
    [documents.length]
  );

  async function handleScan(folderPath: string): Promise<void> {
    setIsScanning(true);
    setScanError(null);
    setPersistStates({});
    try {
      const response = await scanFolder({ folder_path: folderPath });
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

      <FolderScanForm onScan={handleScan} isLoading={isScanning} />

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
