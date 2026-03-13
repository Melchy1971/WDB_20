import type { DocumentScanItem } from "../../types/document";
import type { DocumentAnalysisResult } from "../../types/analysis";
import { PreviewBox } from "./PreviewBox";

export type PersistStatus = "idle" | "saving" | "success" | "error";

const PRIORITY_LABELS: Record<string, string> = {
  low: "Niedrig",
  medium: "Mittel",
  high: "Hoch",
};

type Props = {
  document: DocumentScanItem;
  persistStatus: PersistStatus;
  persistMessage: string;
  analysisResult: DocumentAnalysisResult | null;
  onPersist: () => void;
};

export function DocumentCard({ document, persistStatus, persistMessage, analysisResult, onPersist }: Props) {
  const isSaving = persistStatus === "saving";
  const isDone = persistStatus === "success";
  const canPersist = document.parse_status === "parsed";

  return (
    <article className="card">
      <h3 className="card__title">{document.file_name}</h3>
      <dl className="card__meta">
        <dt>Pfad</dt>
        <dd title={document.file_path}>{document.file_path}</dd>
        <dt>Erweiterung</dt>
        <dd>{document.extension || "&#8212;"}</dd>
        <dt>Parser</dt>
        <dd>{document.parser_type || "&#8212;"}</dd>
        <dt>Status</dt>
        <dd>{document.parse_status || "&#8212;"}</dd>
        <dt>Groesse</dt>
        <dd>{document.size_bytes} Bytes</dd>
        <dt>Geaendert</dt>
        <dd>{document.last_modified}</dd>
      </dl>

      {document.parse_error && (
        <p className="status-message error">{document.parse_error}</p>
      )}

      {document.preview_text && (
        <PreviewBox title="Vorschau" content={document.preview_text} />
      )}

      {analysisResult && (
        <div className="analysis-result">
          <h4 className="analysis-result__title">KI-Analyse</h4>
          <dl className="card__meta">
            <dt>Thema</dt>
            <dd>{analysisResult.topic_label}</dd>
            <dt>Zusammenfassung</dt>
            <dd>{analysisResult.summary}</dd>
            {analysisResult.keywords.length > 0 && (
              <>
                <dt>Schlagworte</dt>
                <dd>{analysisResult.keywords.join(", ")}</dd>
              </>
            )}
            {analysisResult.entities.length > 0 && (
              <>
                <dt>Entitaeten</dt>
                <dd>{analysisResult.entities.join(", ")}</dd>
              </>
            )}
            <dt>Prioritaet</dt>
            <dd>{PRIORITY_LABELS[analysisResult.priority] ?? analysisResult.priority}</dd>
            <dt>Konfidenz</dt>
            <dd>{(analysisResult.confidence * 100).toFixed(0)} %</dd>
          </dl>
        </div>
      )}

      <button
        className="action-button"
        type="button"
        onClick={onPersist}
        disabled={isSaving || isDone || !canPersist}
      >
        {isSaving ? "Speichere ..." : isDone ? "Gespeichert" : "In Neo4j speichern"}
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
