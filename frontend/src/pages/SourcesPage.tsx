import { useEffect, useState } from "react";
import { getSources, createSource } from "../api/sourcesApi";
import { SourceForm } from "../components/SourceForm";
import { StatusBanner } from "../components/StatusBanner";
import type { Source, CreateSourceRequest } from "../types/source";

export function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    getSources()
      .then(setSources)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function handleCreate(data: CreateSourceRequest): Promise<void> {
    setIsCreating(true);
    setError(null);
    try {
      const created = await createSource(data);
      setSources((prev) => [...prev, created]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unbekannter Fehler beim Anlegen der Quelle.");
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <div className="page">
      <h1>Quellen</h1>

      {error && (
        <StatusBanner message={error} variant="error" onDismiss={() => setError(null)} />
      )}

      <section className="panel">
        <h2>Neue Quelle anlegen</h2>
        <SourceForm onSubmit={handleCreate} isLoading={isCreating} />
      </section>

      <section>
        <h2>Vorhandene Quellen</h2>
        {loading && <p className="hint">Lade Quellen ...</p>}
        {!loading && sources.length === 0 && (
          <p className="hint">Noch keine Quellen vorhanden.</p>
        )}
        <div className="card-grid">
          {sources.map((source) => (
            <article className="card" key={source.id}>
              <h3>{source.name}</h3>
              <dl className="card__meta">
                <dt>Typ</dt>
                <dd>{source.type}</dd>
                <dt>Pfad</dt>
                <dd>{source.path}</dd>
                <dt>Erstellt</dt>
                <dd>{source.created_at}</dd>
              </dl>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
