import { useEffect, useState } from "react";

import { fetchImportRun } from "../api/importRunsApi";
import { StatusBanner } from "../components/status/StatusBanner";
import type { ImportRun } from "../types/pstImport";

type LoadState = "idle" | "loading" | "ready" | "error";

type Props = {
  selectedImportRunId: string | null;
};

const IMPORT_RUN_STATUS_LABELS: Record<ImportRun["status"], string> = {
  queued: "In Warteschlange",
  running: "Läuft ...",
  finished: "Abgeschlossen",
  failed: "Fehlgeschlagen",
};

const IMPORT_RUN_STATUS_CLASS: Record<ImportRun["status"], string> = {
  queued: "pending",
  running: "pending",
  finished: "success",
  failed: "error",
};

export function PstImportRunPage({ selectedImportRunId }: Props) {
  const [run, setRun] = useState<ImportRun | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedImportRunId === null) {
      setRun(null);
      setLoadState("idle");
      setLoadError(null);
      return;
    }

    let cancelled = false;
    let timeoutId: ReturnType<typeof setTimeout> | null = null;

    const loadRun = async (isInitialLoad: boolean): Promise<void> => {
      if (isInitialLoad) {
        setLoadState("loading");
        setLoadError(null);
      }

      try {
        const result = await fetchImportRun(selectedImportRunId);
        if (cancelled) {
          return;
        }

        setRun(result);
        setLoadState("ready");
        setLoadError(null);

        if (result.status === "queued" || result.status === "running") {
          timeoutId = setTimeout(() => {
            void loadRun(false);
          }, 2000);
        }
      } catch (err) {
        if (cancelled) {
          return;
        }

        setRun(null);
        setLoadError(err instanceof Error ? err.message : "Fehler beim Laden des ImportRun.");
        setLoadState("error");
      }
    };

    void loadRun(true);

    return () => {
      cancelled = true;
      if (timeoutId !== null) {
        clearTimeout(timeoutId);
      }
    };
  }, [selectedImportRunId]);

  return (
    <div className="page">
      <h1>PST-ImportRun Ergebnis</h1>

      {selectedImportRunId === null && (
        <p className="hint">Kein ImportRun ausgewählt. Starten Sie zuerst einen PST-Import.</p>
      )}

      {loadState === "loading" && (
        <p className="status-message pending">ImportRun wird geladen ...</p>
      )}

      {loadState === "error" && loadError && (
        <StatusBanner message={loadError} variant="error" />
      )}

      {loadState === "ready" && run !== null && (
        <div className="panel">
          <h2>ImportRun</h2>
          <dl className="card__meta">
            <dt>ImportRun-ID</dt>
            <dd>{run.import_run_id}</dd>
            <dt>Status</dt>
            <dd>
              <span className={`job-status-badge ${IMPORT_RUN_STATUS_CLASS[run.status]}`}>
                {IMPORT_RUN_STATUS_LABELS[run.status]}
              </span>
            </dd>
            <dt>E-Mails</dt>
            <dd>{run.email_count}</dd>
            <dt>Attachments</dt>
            <dd>{run.attachment_count}</dd>
            <dt>Fehler</dt>
            <dd>{run.error_message ?? "-"}</dd>
          </dl>

          {run.imported_emails.length === 0 ? (
            <p className="hint">Keine importierten E-Mails vorhanden.</p>
          ) : (
            <div className="imported-email-list">
              {run.imported_emails.map((mail) => (
                <article className="card" key={mail.message_id}>
                  <h3 className="card__title">{mail.subject ?? "(ohne Betreff)"}</h3>
                  <dl className="card__meta">
                    <dt>Message-ID</dt>
                    <dd>{mail.message_id}</dd>
                    <dt>Von</dt>
                    <dd>{mail.sender ?? "-"}</dd>
                    <dt>An</dt>
                    <dd>{mail.recipients.join(", ") || "-"}</dd>
                    <dt>Gesendet</dt>
                    <dd>{mail.sent_at ?? "-"}</dd>
                    <dt>Ordner</dt>
                    <dd>{mail.source_folder_path}</dd>
                    <dt>Attachments</dt>
                    <dd>{mail.attachments.length}</dd>
                  </dl>

                  {mail.attachments.length > 0 && (
                    <div className="preview-panel">
                      <p className="preview-panel__title">Attachment-Metadaten</p>
                      <div className="preview-box">
                        {mail.attachments
                          .map((attachment) => {
                            const mime = attachment.mime_type ?? "unknown";
                            const size = attachment.size_bytes ?? 0;
                            return `${attachment.file_name} (${mime}, ${size} bytes)`;
                          })
                          .join("\n")}
                      </div>
                    </div>
                  )}

                  <div className="preview-panel">
                    <p className="preview-panel__title">Body</p>
                    <div className="preview-box">{mail.body_text || "(leer)"}</div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
