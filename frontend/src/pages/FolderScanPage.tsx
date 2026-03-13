import { useMemo, useState } from "react";
import { persistDocument } from "../api/persistApi";
import { analyzeScan, scanSource } from "../api/sourcesApi";
import { DocumentList } from "../components/documents/DocumentList";
import { StatusBanner } from "../components/status/StatusBanner";
import type { DocumentScanItem } from "../types/document";
import type { PersistStatus } from "../components/documents/DocumentCard";
import type { DocumentAnalysisResult } from "../types/analysis";

type PersistState = {
  status: PersistStatus;
  message: string;
};

type Props = {
  selectedSourceId: string | null;
  selectedSourceType: string | null;
  onNavigateToPstImport: () => void;
};

export function FolderScanPage({ selectedSourceId, selectedSourceType, onNavigateToPstImport }: Props) {
  const [documents, setDocuments] = useState<DocumentScanItem[]>([]);
  const [scanId, setScanId] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanError, setScanError] = useState<string | null>(null);
  const [persistStates, setPersistStates] = useState<Record<string, PersistState>>({});
  const [analysisResults, setAnalysisResults] = useState<Record<string, DocumentAnalysisResult>>({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

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
    setAnalysisResults({});
    setAnalysisError(null);
    try {
      const response = await scanSource(selectedSourceId);
      setScanId(response.scan_id);
      setDocuments(response.items);
      const parsedCount = response.items.filter((i) => i.parse_status === "parsed").length;
      if (parsedCount > 0) {
        await runAnalysis(response.scan_id);
      }
    } catch (err) {
      setDocuments([]);
      setScanError(err instanceof Error ? err.message : "Unbekannter Fehler beim Scannen.");
    } finally {
      setIsScanning(false);
    }
  }

  async function runAnalysis(id: string): Promise<void> {
    setIsAnalyzing(true);
    setAnalysisError(null);
    try {
      const response = await analyzeScan(id);
      const byId: Record<string, DocumentAnalysisResult> = {};
      for (const result of response.results) {
        byId[result.document_id] = result;
      }
      setAnalysisResults(byId);
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : "Fehler bei der KI-Analyse.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function handlePersist(doc: DocumentScanItem): Promise<void> {
    if (scanId === null) return;
    setPersistStates((prev) => ({
      ...prev,
      [doc.document_id]: { status: "saving", message: "Speicherung laeuft ..." },
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
          <p className="hint">Keine Quelle aktiv. Waehlen Sie zuerst eine Quelle in der Quellenverwaltung.</p>
        ) : selectedSourceType === "PST" ? (
          <div>
            <p className="status-message pending">Aktive Quelle: {selectedSourceId}</p>
            <p className="hint">PST-Dateien werden ueber den PST-Import verarbeitet.</p>
            <button
              type="button"
              className="action-button"
              onClick={onNavigateToPstImport}
            >
              Zum PST-Import
            </button>
          </div>
        ) : (
          <p className="status-message pending">Aktive Quelle: {selectedSourceId}</p>
        )}
        {selectedSourceType !== "PST" && (
          <button
            className="action-button"
            type="submit"
            disabled={isScanning || isAnalyzing || selectedSourceId === null}
          >
            {isScanning ? "Scanne ..." : isAnalyzing ? "KI analysiert ..." : "Quelle scannen"}
          </button>
        )}
      </form>

      {scanError && (
        <StatusBanner message={scanError} variant="error" onDismiss={() => setScanError(null)} />
      )}
      {analysisError && (
        <StatusBanner message={analysisError} variant="error" onDismiss={() => setAnalysisError(null)} />
      )}
      {scanSummary && !isScanning && (
        <StatusBanner
          message={
            isAnalyzing
              ? `${scanSummary} KI-Analyse laeuft ...`
              : `${scanSummary}${Object.keys(analysisResults).length > 0 ? ` ${Object.keys(analysisResults).length} Dokument(e) analysiert.` : ""}`
          }
          variant={isAnalyzing ? "info" : "success"}
        />
      )}

      <DocumentList
        documents={documents}
        persistStates={persistStates}
        analysisResults={analysisResults}
        onPersist={handlePersist}
        isScanning={isScanning}
      />
    </div>
  );
}
