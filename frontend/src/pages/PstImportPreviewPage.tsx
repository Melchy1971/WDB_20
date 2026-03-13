import { useEffect, useState } from "react";
import { fetchImportPreview } from "../api/importPreviewApi";
import { fetchImportJobStatus, startImportJob } from "../api/importJobsApi";
import { StatusBanner } from "../components/status/StatusBanner";
import type { ImportPreviewItem, ImportPreviewResponse } from "../types/importPreview";
import type { ImportJobResponse, JobStatus } from "../types/job";
import type { TreeNodeType } from "../types/tree";

type LoadState = "idle" | "loading" | "ready" | "error";
type JobState = "idle" | "starting" | "ready" | "refreshing" | "error";

const NODE_ICONS: Record<TreeNodeType, string> = {
  folder: ">",
  message: "✉",
  attachment: "⊘",
};

const NODE_TYPE_LABELS: Record<TreeNodeType, string> = {
  folder: "Ordner",
  message: "Nachricht",
  attachment: "Anhang",
};

const JOB_STATUS_LABELS: Record<JobStatus, string> = {
  queued: "In Warteschlange",
  running: "Läuft ...",
  finished: "Abgeschlossen",
  failed: "Fehlgeschlagen",
};

const JOB_STATUS_CLASS: Record<JobStatus, string> = {
  queued: "pending",
  running: "pending",
  finished: "success",
  failed: "error",
};

type Props = {
  selectedSourceId: string | null;
  onOpenImportRun: (importRunId: string) => void;
};

function PreviewItem({ item }: { item: ImportPreviewItem }) {
  return (
    <div className="preview-item">
      <span className="preview-item__icon" aria-hidden="true">
        {NODE_ICONS[item.node_type]}
      </span>
      <span className="preview-item__name">{item.node_name}</span>
      <span className="preview-item__type">{NODE_TYPE_LABELS[item.node_type]}</span>
    </div>
  );
}

function JobPanel({
  job,
  jobState,
  jobError,
  onRefresh,
}: {
  job: ImportJobResponse;
  jobState: JobState;
  jobError: string | null;
  onRefresh: () => void;
}) {
  return (
    <div className="panel">
      <h2>Import-Job</h2>
      <dl className="card__meta">
        <dt>Job-ID</dt>
        <dd>{job.job_id}</dd>
        <dt>Status</dt>
        <dd>
          <span className={`job-status-badge ${JOB_STATUS_CLASS[job.status]}`}>
            {JOB_STATUS_LABELS[job.status]}
          </span>
        </dd>
        <dt>ImportRun-ID</dt>
        <dd>{job.import_run_id ?? "-"}</dd>
        <dt>Elemente</dt>
        <dd>{job.selected_count}</dd>
        <dt>Meldung</dt>
        <dd>{job.message}</dd>
      </dl>

      {jobError && <p className="status-message error">{jobError}</p>}

      <div className="action-bar">
        <button
          type="button"
          className="action-button action-button--secondary"
          onClick={onRefresh}
          disabled={jobState === "refreshing"}
        >
          {jobState === "refreshing" ? "Wird aktualisiert ..." : "Status aktualisieren"}
        </button>
      </div>
    </div>
  );
}

export function PstImportPreviewPage({ selectedSourceId, onOpenImportRun }: Props) {
  const [preview, setPreview] = useState<ImportPreviewResponse | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [loadError, setLoadError] = useState<string | null>(null);

  const [job, setJob] = useState<ImportJobResponse | null>(null);
  const [jobState, setJobState] = useState<JobState>("idle");
  const [jobError, setJobError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedSourceId === null) {
      setLoadState("idle");
      setPreview(null);
      setJob(null);
      setJobState("idle");
      setJobError(null);
      return;
    }

    setLoadState("loading");
    setPreview(null);
    setLoadError(null);

    fetchImportPreview(selectedSourceId)
      .then((res) => {
        setPreview(res);
        setLoadState("ready");
      })
      .catch((err: unknown) => {
        setLoadError(
          err instanceof Error ? err.message : "Fehler beim Laden der Import-Vorschau."
        );
        setLoadState("error");
      });
  }, [selectedSourceId]);

  async function handleStartImport(): Promise<void> {
    if (selectedSourceId === null) return;

    setJobState("starting");
    setJobError(null);

    try {
      const started = await startImportJob(selectedSourceId);
      setJob(started);
      setJobState("ready");
      if (started.import_run_id !== null) {
        onOpenImportRun(started.import_run_id);
      }
    } catch (err) {
      setJobError(err instanceof Error ? err.message : "Fehler beim Starten des Import-Jobs.");
      setJobState("error");
    }
  }

  async function handleRefreshStatus(): Promise<void> {
    if (job === null) return;

    setJobState("refreshing");
    setJobError(null);

    try {
      const updated = await fetchImportJobStatus(job.job_id);
      setJob(updated);
      setJobState("ready");
    } catch (err) {
      setJobError(err instanceof Error ? err.message : "Fehler beim Abrufen des Job-Status.");
      setJobState("ready");
    }
  }

  const isJobStarting = jobState === "starting";
  const canStartImport =
    loadState === "ready" &&
    preview !== null &&
    preview.status === "ready" &&
    !isJobStarting &&
    (jobState === "idle" || jobState === "error");

  return (
    <div className="page">
      <h1>PST-Import-Vorschau</h1>

      {selectedSourceId === null && (
        <p className="hint">
          Keine Quelle aktiv. Wählen Sie zuerst eine PST-Quelle in der Quellenverwaltung.
        </p>
      )}

      {loadState === "loading" && (
        <p className="status-message pending">Vorschau wird geladen ...</p>
      )}

      {loadState === "error" && loadError && (
        <StatusBanner message={loadError} variant="error" />
      )}

      {loadState === "ready" && preview !== null && (
        <div className="panel">
          <h2>Vorschau</h2>
          {preview.status === "empty" ? (
            <p className="hint">
              Keine Knoten ausgewählt. Wählen Sie Knoten in der PST-Struktur aus und speichern Sie
              die Auswahl.
            </p>
          ) : (
            <>
              <p className="preview-summary">
                {preview.selected_count}{" "}
                {preview.selected_count === 1 ? "Knoten" : "Knoten"} zur Vorschau bereit.
              </p>
              <div className="preview-list">
                {preview.items.map((item) => (
                  <PreviewItem key={item.node_id} item={item} />
                ))}
              </div>
            </>
          )}

          {jobState === "error" && jobError && (
            <p className="status-message error">{jobError}</p>
          )}

          <div className="action-bar">
            <button
              type="button"
              className="action-button"
              onClick={handleStartImport}
              disabled={!canStartImport}
            >
              {isJobStarting ? "Import wird gestartet ..." : "Import starten"}
            </button>
          </div>
        </div>
      )}

      {job !== null && (
        <JobPanel
          job={job}
          jobState={jobState}
          jobError={jobError}
          onRefresh={handleRefreshStatus}
        />
      )}
    </div>
  );
}
