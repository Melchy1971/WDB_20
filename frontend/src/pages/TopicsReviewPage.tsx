import { useEffect, useState } from "react";
import { getTopics, reviewTopic } from "../api/topicsApi";
import { TopicReviewPanel } from "../components/TopicReviewPanel";
import { StatusBanner } from "../components/StatusBanner";
import type { Topic } from "../types/source";

export function TopicsReviewPage() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [processingId, setProcessingId] = useState<string | null>(null);

  useEffect(() => {
    getTopics()
      .then(setTopics)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function handleReview(topicId: string, action: "approve" | "reject"): Promise<void> {
    setProcessingId(topicId);
    setError(null);
    try {
      const updated = await reviewTopic({ topic_id: topicId, action });
      setTopics((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Fehler bei der Themenbewertung."
      );
    } finally {
      setProcessingId(null);
    }
  }

  return (
    <div className="page">
      <h1>Themen prüfen</h1>

      {error && (
        <StatusBanner message={error} variant="error" onDismiss={() => setError(null)} />
      )}

      {loading && <p className="hint">Lade Themen ...</p>}

      {!loading && topics.length === 0 && (
        <p className="hint">Keine Themen zur Überprüfung vorhanden.</p>
      )}

      <div className="card-grid">
        {topics.map((topic) => (
          <TopicReviewPanel
            key={topic.id}
            topic={topic}
            onApprove={(id) => handleReview(id, "approve")}
            onReject={(id) => handleReview(id, "reject")}
            isProcessing={processingId === topic.id}
          />
        ))}
      </div>
    </div>
  );
}
