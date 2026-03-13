import type { DocumentScanItem } from "../../types/document";
import { DocumentCard } from "./DocumentCard";
import type { PersistStatus } from "./DocumentCard";
import type { DocumentAnalysisResult } from "../../types/analysis";

type PersistState = {
  status: PersistStatus;
  message: string;
};

type Props = {
  documents: DocumentScanItem[];
  persistStates: Record<string, PersistState>;
  analysisResults: Record<string, DocumentAnalysisResult>;
  onPersist: (document: DocumentScanItem) => void;
  isScanning: boolean;
};

export function DocumentList({ documents, persistStates, analysisResults, onPersist, isScanning }: Props) {
  return (
    <section>
      <h2>Gefundene Dokumente</h2>
      {documents.length === 0 && !isScanning && (
        <p className="hint">Noch keine Dateien geladen.</p>
      )}
      <div className="card-grid">
        {documents.map((doc) => {
          const ps = persistStates[doc.document_id] ?? { status: "idle", message: "" };
          return (
            <DocumentCard
              key={doc.document_id}
              document={doc}
              persistStatus={ps.status}
              persistMessage={ps.message}
              analysisResult={analysisResults[doc.document_id] ?? null}
              onPersist={() => onPersist(doc)}
            />
          );
        })}
      </div>
    </section>
  );
}
