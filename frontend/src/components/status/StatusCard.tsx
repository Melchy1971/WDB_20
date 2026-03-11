type StatusVariant = "ok" | "degraded" | "down" | "unknown";

type Props = {
  label: string;
  value: string;
  variant?: StatusVariant;
};

function resolveVariant(value: string): StatusVariant {
  const v = value.toLowerCase();
  if (v === "ok" || v === "healthy" || v === "connected") return "ok";
  if (v === "degraded" || v === "slow") return "degraded";
  if (v === "down" || v === "error" || v === "disconnected") return "down";
  return "unknown";
}

const VARIANT_LABELS: Record<StatusVariant, string> = {
  ok: "●",
  degraded: "◑",
  down: "○",
  unknown: "–",
};

export function StatusCard({ label, value, variant }: Props) {
  const resolved = variant ?? resolveVariant(value);
  return (
    <div className={`status-card status-card--${resolved}`}>
      <span className="status-card__indicator" aria-hidden="true">
        {VARIANT_LABELS[resolved]}
      </span>
      <div className="status-card__body">
        <span className="status-card__label">{label}</span>
        <span className="status-card__value">{value}</span>
      </div>
    </div>
  );
}
