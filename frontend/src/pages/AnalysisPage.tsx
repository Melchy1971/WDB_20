import { useState } from "react";

import { fetchImportRunAnalysisResults, startImportRunAnalysis } from "../api/analysisApi";
import { StatusBanner } from "../components/status/StatusBanner";
import type { AnalysisResult } from "../types/analysis";

type Props = {
  importRunId: string | null;
};

type AnalysisLoadState = "idle" | "loading" | "ready" | "error";

export function AnalysisPage({ importRunId }: Props) {
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [analysisStatus, setAnalysisStatus] = useState<string | null>(null);
  const [startMessage, setStartMessage] = useState<string | null>(null);
  const [loadState, setLoadState] = useState<AnalysisLoadState>("idle");
  const [error, setError] = useState<string | null>(null);

  const disabled = importRunId === null;

  async function handleStartAnalysis(): Promise<void> {
    if (importRunId === null) return;
    setLoadState("loading");
    setError(null);
    setStartMessage(null);
    try {
      const response = await startImportRunAnalysis(importRunId);
      setAnalysisStatus(response.status);
      setStartMessage(response.message);
      setLoadState("ready");
    } catch (err) {
      setLoadState("error");
      setError(err instanceof Error ? err.message : "Fehler beim Starten der Analyse.");
    }
  }

  async function handleLoadResults(): Promise<void> {
    if (importRunId === null) return;
    setLoadState("loading");
    setError(null);
    try {
      const response = await fetchImportRunAnalysisResults(importRunId);
      setAnalysisStatus(response.status);
      setResults(response.results);
      setLoadState("ready");
    } catch (err) {
      setLoadState("error");
      setError(err instanceof Error ? err.message : "Fehler beim Laden der Analyseergebnisse.");
    }
  }

  return (
    <div className="page">
      <h1>ImportRun-Analyse</h1>

      {importRunId === null && (
        <p className="hint">Kein ImportRun ausgewählt. Starten Sie zuerst einen PST-Import.</p>
      )}

      {importRunId !== null && (
        <div className="panel">
          <h2>Analyse-Steuerung</h2>
          <dl className="card__meta">
            <dt>ImportRun-ID</dt>
            <dd>{importRunId}</dd>
            <dt>Analyse-Status</dt>
            <dd>{analysisStatus ?? "-"}</dd>
          </dl>

          {startMessage && <p className="status-message success">{startMessage}</p>}
          {loadState === "loading" && (
            <p className="status-message pending">Analyseaktion wird ausgeführt …</p>
          )}
          {loadState === "error" && error && <StatusBanner message={error} variant="error" />}

          <div className="action-bar">
            <button
              type="button"
              className="action-button"
              onClick={handleStartAnalysis}
              disabled={disabled || loadState === "loading"}
            >
              Analyse starten
            </button>
            <button
              type="button"
              className="action-button action-button--secondary"
              onClick={handleLoadResults}
              disabled={disabled || loadState === "loading"}
            >
              Ergebnisse laden
            </button>
          </div>
        </div>
      )}

      <div className="panel">
        <h2>Analyseergebnisse</h2>
        {results.length === 0 ? (
          <p className="hint">Noch keine Analyseergebnisse geladen.</p>
        ) : (
          <div className="imported-email-list">
            {results.map((result, index) => (
              <article className="card" key={`${result.topic_label}-${index}`}>
                <h3 className="card__title">{result.topic_label}</h3>
                <dl className="card__meta">
                  <dt>Summary</dt>
                  <dd>{result.summary}</dd>
                  <dt>Keywords</dt>
                  <dd>{result.keywords.join(", ") || "-"}</dd>
                  <dt>Entities</dt>
                  <dd>{result.entities.join(", ") || "-"}</dd>
                  <dt>Priority</dt>
                  <dd>{result.priority}</dd>
                  <dt>Confidence</dt>
                  <dd>{result.confidence}</dd>
                </dl>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
