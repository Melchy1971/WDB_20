import { useMemo, useState } from "react";
import { persistDocument } from "../api/persistApi";
import { scanFolder } from "../api/sourcesApi";
import { DocumentCard } from "../components/DocumentCard";
import { FolderScanForm } from "../components/FolderScanForm";
import { StatusBanner } from "../components/StatusBanner";
import type { DocumentItem } from "../types/document";
import type { PersistStatus } from "../components/DocumentCard";

type PersistState = {
  status: PersistStatus;
  message: string;
};

export function FolderScanPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
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
      setScanError(
        err instanceof Error ? err.message : "Unbekannter Fehler beim Scannen."
      );
    } finally {
      setIsScanning(false);
    }
  }

  async function handlePersist(document: DocumentItem): Promise<void> {
    setPersistStates((prev) => ({
      ...prev,
      [document.file_path]: { status: "saving", message: "Speicherung läuft ..." },
    }));
    try {
      const response = await persistDocument(document);
      setPersistStates((prev) => ({
        ...prev,
        [document.file_path]: {
          status: "success",
          message: `Erfolgreich gespeichert: ${response.file_path}`,
        },
      }));
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Unbekannter Fehler beim Speichern.";
      setPersistStates((prev) => ({
        ...prev,
        [document.file_path]: { status: "error", message },
      }));
    }
  }

  return (
    <div className="page">
      <h1>Dokumentenimport</h1>

      <FolderScanForm onScan={handleScan} isLoading={isScanning} />

      {scanError && (
        <StatusBanner
          message={scanError}
          variant="error"
          onDismiss={() => setScanError(null)}
        />
      )}
      {scanSummary && <StatusBanner message={scanSummary} variant="success" />}

      <section>
        <h2>Gefundene Dokumente</h2>
        {documents.length === 0 && !isScanning && (
          <p className="hint">Noch keine Dateien geladen.</p>
        )}
        <div className="card-grid">
          {documents.map((doc) => {
            const ps = persistStates[doc.file_path] ?? { status: "idle", message: "" };
            return (
              <DocumentCard
                key={doc.file_path}
                document={doc}
                persistStatus={ps.status}
                persistMessage={ps.message}
                onPersist={() => handlePersist(doc)}
              />
            );
          })}
        </div>
      </section>
    </div>
  );
}
