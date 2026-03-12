export type JobStatus = "queued" | "running" | "finished" | "failed";
export type JobType = "PST_IMPORT";

/**
 * Gemeinsame Felder beider Import-Job-Endpunkte.
 * Bildet die Schnittmenge ab, die garantiert immer vorhanden ist.
 * StartImportJobResponse und ImportJobStatusResponse können in Zukunft
 * unabhängig voneinander um endpunkt-spezifische Felder erweitert werden.
 */
export type ImportJobResponse = {
  job_id: string;
  source_id: string;
  job_type: JobType;
  status: JobStatus;
  import_run_id: string | null;
  selected_count: number;
  error_message: string | null;
  message: string;
};

/**
 * Antwort auf POST /sources/{source_id}/import-jobs.
 * Reserviert für zukünftige Felder wie queue_position.
 */
export type StartImportJobResponse = ImportJobResponse;

/**
 * Antwort auf GET /import-jobs/{job_id}.
 * Reserviert für zukünftige Felder wie progress_percent.
 */
export type ImportJobStatusResponse = ImportJobResponse;
