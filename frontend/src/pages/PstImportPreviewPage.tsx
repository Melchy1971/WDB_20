import { useEffect, useState } from "react";
import { fetchImportPreview } from "../api/importPreviewApi";
import { StatusBanner } from "../components/status/StatusBanner";
import type { ImportPreviewItem, ImportPreviewResponse } from "../types/importPreview";
import type { TreeNodeType } from "../types/tree";

type LoadState = "idle" | "loading" | "ready" | "error";

const NODE_ICONS: Record<TreeNodeType, string> = {
  folder: "▶",
  message: "✉",
  attachment: "⊘",
};

const NODE_TYPE_LABELS: Record<TreeNodeType, string> = {
  folder: "Ordner",
  message: "Nachricht",
  attachment: "Anhang",
};

type Props = {
  selectedSourceId: string | null;
};

function PreviewItem({ item }: { item: ImportPreviewItem }) {
  return (
    <div className="preview-item">
      <span className="preview-item__icon" aria-hidden="true">
        {NODE_ICONS[item.node_type]}
      </span>
      <span className="preview-item__name">{item.node_name}</span>
      <span className="preview-item__type">{NODE_TYPE_LABELS[item.node_type]}</span>
    </div>
  );
}

export function PstImportPreviewPage({ selectedSourceId }: Props) {
  const [preview, setPreview] = useState<ImportPreviewResponse | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedSourceId === null) {
      setLoadState("idle");
      setPreview(null);
      return;
    }
    setLoadState("loading");
    setPreview(null);
    setLoadError(null);
    fetchImportPreview(selectedSourceId)
      .then((res) => {
        setPreview(res);
        setLoadState("ready");
      })
      .catch((err: unknown) => {
        setLoadError(
          err instanceof Error ? err.message : "Fehler beim Laden der Import-Vorschau."
        );
        setLoadState("error");
      });
  }, [selectedSourceId]);

  return (
    <div className="page">
      <h1>PST-Import-Vorschau</h1>

      {selectedSourceId === null && (
        <p className="hint">
          Keine Quelle aktiv. Wählen Sie zuerst eine PST-Quelle in der Quellenverwaltung.
        </p>
      )}

      {loadState === "loading" && (
        <p className="status-message pending">Vorschau wird geladen ...</p>
      )}

      {loadState === "error" && loadError && (
        <StatusBanner message={loadError} variant="error" />
      )}

      {loadState === "ready" && preview !== null && (
        <div className="panel">
          {preview.status === "empty" ? (
            <p className="hint">
              Keine Knoten ausgewählt. Wählen Sie Knoten in der PST-Struktur aus und speichern Sie
              die Auswahl.
            </p>
          ) : (
            <>
              <p className="preview-summary">
                {preview.selected_count}{" "}
                {preview.selected_count === 1 ? "Knoten" : "Knoten"} zur Vorschau bereit.
              </p>
              <div className="preview-list">
                {preview.items.map((item) => (
                  <PreviewItem key={item.node_id} item={item} />
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
