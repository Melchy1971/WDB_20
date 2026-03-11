import type { DocumentItem } from "../../types/document";
import { PreviewBox } from "./PreviewBox";

export type PersistStatus = "idle" | "saving" | "success" | "error";

type Props = {
  document: DocumentItem;
  persistStatus: PersistStatus;
  persistMessage: string;
  onPersist: () => void;
};

export function DocumentCard({ document, persistStatus, persistMessage, onPersist }: Props) {
  const isSaving = persistStatus === "saving";
  const isDone = persistStatus === "success";

  return (
    <article className="card">
      <h3 className="card__title">{document.file_name}</h3>
      <dl className="card__meta">
        <dt>Pfad</dt>
        <dd title={document.file_path}>{document.file_path}</dd>
        <dt>Erweiterung</dt>
        <dd>{document.extension || "—"}</dd>
        <dt>Parser</dt>
        <dd>{document.parser_type || "—"}</dd>
        <dt>Status</dt>
        <dd>{document.parse_status || "—"}</dd>
        <dt>Größe</dt>
        <dd>{document.size_bytes} Bytes</dd>
        <dt>Geändert</dt>
        <dd>{document.last_modified}</dd>
      </dl>

      {document.preview_text && (
        <PreviewBox title="Vorschau" content={document.preview_text} />
      )}

      <button
        className="action-button"
        type="button"
        onClick={onPersist}
        disabled={isSaving || isDone}
      >
        {isSaving ? "Speichere ..." : isDone ? "Gespeichert ✓" : "In Neo4j speichern"}
      </button>

      {persistMessage && (
        <p
          className={`status-message ${
            persistStatus === "success"
              ? "success"
              : persistStatus === "error"
                ? "error"
                : "pending"
          }`}
        >
          {persistMessage}
        </p>
      )}
    </article>
  );
}
