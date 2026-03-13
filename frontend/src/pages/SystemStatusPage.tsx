import { useEffect, useState } from "react";
import { getHealth } from "../api/systemApi";
import { StatusCard } from "../components/status/StatusCard";
import { StatusBanner } from "../components/status/StatusBanner";
import type { HealthResponse } from "../types/system";

export function SystemStatusPage() {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then((result) => {
        setData(result);
        setError(null);
      })
      .catch((err: Error) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <div className="page">
      <h1>System Status</h1>

      {loading && <p className="hint">Lade Systemstatus ...</p>}

      {error && (
        <StatusBanner
          message={error}
          variant="error"
          onDismiss={() => setError(null)}
        />
      )}

      {data && (
        <div className="card-grid">
          <StatusCard label="API" value={data.api_status} />
          <StatusCard label="Neo4j" value={data.neo4j_status} />
          <StatusCard label="Ollama" value={data.ollama_status} />
          <StatusCard label="Environment" value={data.environment} />
          <StatusCard label="Erfasste Dokumente" value={String(data.document_count)} />
        </div>
      )}
    </div>
  );
}
