import type { Topic } from "../types/source";

type Props = {
  topic: Topic;
  onApprove: (topicId: string) => void;
  onReject: (topicId: string) => void;
  isProcessing: boolean;
};

const STATUS_LABEL: Record<Topic["status"], string> = {
  pending: "Ausstehend",
  reviewed: "Bestätigt",
  rejected: "Abgelehnt",
};

export function TopicReviewPanel({ topic, onApprove, onReject, isProcessing }: Props) {
  const isPending = topic.status === "pending";

  return (
    <article className="card">
      <h3 className="card__title">{topic.label}</h3>
      <p className="card__description">{topic.description}</p>
      <p className="hint">{topic.document_count} Dokument(e)</p>

      <div className="action-bar">
        <button
          className="action-button"
          type="button"
          onClick={() => onApprove(topic.id)}
          disabled={isProcessing || !isPending}
        >
          {isProcessing ? "..." : "Bestätigen"}
        </button>
        <button
          className="action-button action-button--danger"
          type="button"
          onClick={() => onReject(topic.id)}
          disabled={isProcessing || !isPending}
        >
          Ablehnen
        </button>
      </div>

      {!isPending && (
        <p
          className={`status-message ${topic.status === "reviewed" ? "success" : "error"}`}
        >
          {STATUS_LABEL[topic.status]}
        </p>
      )}
    </article>
  );
}
