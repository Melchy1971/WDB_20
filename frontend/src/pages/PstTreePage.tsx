import { useEffect, useState } from "react";
import { fetchSelection, saveSelection } from "../api/sourceSelectionApi";
import { fetchSourceTree } from "../api/sourcesApi";
import { SourceTreeView } from "../components/sources/SourceTreeView";
import { StatusBanner } from "../components/status/StatusBanner";
import type { TreeNode } from "../types/tree";

type LoadState = "idle" | "loading" | "ready" | "error";
type SaveState = "idle" | "saving" | "success" | "error";

type Props = {
  selectedSourceId: string | null;
};

export function PstTreePage({ selectedSourceId }: Props) {
  const [root, setRoot] = useState<TreeNode | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [loadError, setLoadError] = useState<string | null>(null);

  const [selectedNodeIds, setSelectedNodeIds] = useState<string[]>([]);
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  useEffect(() => {
    if (selectedSourceId === null) {
      setLoadState("idle");
      setRoot(null);
      setSelectedNodeIds([]);
      return;
    }
    setLoadState("loading");
    setRoot(null);
    setSelectedNodeIds([]);
    setLoadError(null);
    setSaveState("idle");
    setSaveMessage(null);

    Promise.all([
      fetchSourceTree(selectedSourceId),
      fetchSelection(selectedSourceId),
    ])
      .then(([treeRes, selectionRes]) => {
        setRoot(treeRes.root);
        setSelectedNodeIds(selectionRes.selected_node_ids);
        setLoadState("ready");
      })
      .catch((err: unknown) => {
        setLoadError(
          err instanceof Error ? err.message : "Fehler beim Laden der PST-Struktur."
        );
        setLoadState("error");
      });
  }, [selectedSourceId]);

  function handleToggleNode(nodeId: string): void {
    setSelectedNodeIds((prev) =>
      prev.includes(nodeId) ? prev.filter((id) => id !== nodeId) : [...prev, nodeId]
    );
  }

  async function handleSave(): Promise<void> {
    if (selectedSourceId === null) return;
    setSaveState("saving");
    setSaveMessage(null);
    try {
      const res = await saveSelection(selectedSourceId, selectedNodeIds);
      setSelectedNodeIds(res.selected_node_ids);
      setSaveState("success");
      setSaveMessage(`${res.selected_node_ids.length} Knoten gespeichert.`);
    } catch (err) {
      setSaveState("error");
      setSaveMessage(
        err instanceof Error ? err.message : "Fehler beim Speichern der Auswahl."
      );
    }
  }

  return (
    <div className="page">
      <h1>PST-Struktur</h1>

      {selectedSourceId === null && (
        <p className="hint">
          Keine Quelle aktiv. Wählen Sie zuerst eine PST-Quelle in der Quellenverwaltung.
        </p>
      )}

      {loadState === "loading" && (
        <p className="status-message pending">Struktur wird geladen ...</p>
      )}

      {loadState === "error" && loadError && (
        <StatusBanner message={loadError} variant="error" />
      )}

      {saveMessage && (
        <StatusBanner
          message={saveMessage}
          variant={saveState === "success" ? "success" : "error"}
          onDismiss={() => setSaveMessage(null)}
        />
      )}

      {loadState === "ready" && root !== null && (
        <div className="panel">
          <div className="panel-actions">
            <span className="hint">
              {selectedNodeIds.length === 0
                ? "Keine Knoten ausgewählt"
                : `${selectedNodeIds.length} Knoten ausgewählt`}
            </span>
            <button
              type="button"
              className="action-button"
              onClick={handleSave}
              disabled={saveState === "saving"}
            >
              {saveState === "saving" ? "Speichern ..." : "Auswahl speichern"}
            </button>
          </div>
          <SourceTreeView
            root={root}
            selectedNodeIds={selectedNodeIds}
            onToggleNode={handleToggleNode}
          />
        </div>
      )}
    </div>
  );
}
