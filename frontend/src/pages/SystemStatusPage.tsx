import { useEffect, useState } from "react";
import { getHealth } from "../api/systemApi";
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

  if (loading) {
    return <div className="page">Lade Systemstatus ...</div>;
  }

  if (error) {
    return <div className="page error">Fehler: {error}</div>;
  }

  return (
    <div className="page">
      <h1>System Status</h1>
      <div className="card-grid">
        <div className="card">
          <h2>API</h2>
          <p>{data?.api_status}</p>
        </div>
        <div className="card">
          <h2>Neo4j</h2>
          <p>{data?.neo4j_status}</p>
        </div>
        <div className="card">
          <h2>Ollama</h2>
          <p>{data?.ollama_status}</p>
        </div>
        <div className="card">
          <h2>Environment</h2>
          <p>{data?.environment}</p>
        </div>
      </div>
    </div>
  );
}
