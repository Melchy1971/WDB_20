import type { DocumentScanItem } from "../../types/document";
import { DocumentCard } from "./DocumentCard";
import type { PersistStatus } from "./DocumentCard";

type PersistState = {
  status: PersistStatus;
  message: string;
};

type Props = {
  documents: DocumentScanItem[];
  persistStates: Record<string, PersistState>;
  onPersist: (document: DocumentScanItem) => void;
  isScanning: boolean;
};

export function DocumentList({ documents, persistStates, onPersist, isScanning }: Props) {
  return (
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
              onPersist={() => onPersist(doc)}
            />
          );
        })}
      </div>
    </section>
  );
}
