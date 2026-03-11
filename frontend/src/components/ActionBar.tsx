type ActionVariant = "primary" | "danger";

export type ActionBarItem = {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  variant?: ActionVariant;
};

type Props = {
  actions: ActionBarItem[];
};

export function ActionBar({ actions }: Props) {
  return (
    <div className="action-bar">
      {actions.map((action) => (
        <button
          key={action.label}
          className={`action-button${action.variant === "danger" ? " action-button--danger" : ""}`}
          type="button"
          onClick={action.onClick}
          disabled={action.disabled}
        >
          {action.label}
        </button>
      ))}
    </div>
  );
}
