type Variant = "info" | "success" | "error" | "warning";

type Props = {
  message: string;
  variant?: Variant;
  onDismiss?: () => void;
};

const CLASS_MAP: Record<Variant, string> = {
  info: "pending",
  success: "success",
  error: "error",
  warning: "pending",
};

export function StatusBanner({ message, variant = "info", onDismiss }: Props) {
  return (
    <div
      className={`status-banner status-message ${CLASS_MAP[variant]}`}
      role="alert"
      aria-live="polite"
    >
      <span className="status-banner__text">{message}</span>
      {onDismiss && (
        <button
          className="status-banner__dismiss"
          type="button"
          onClick={onDismiss}
          aria-label="Meldung schließen"
        >
          ×
        </button>
      )}
    </div>
  );
}
