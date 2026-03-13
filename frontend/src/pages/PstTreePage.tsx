import { useEffect, useMemo, useState } from "react";

import { fetchSelection, saveSelection } from "../api/sourceSelectionApi";
import { fetchSourceTree } from "../api/sourcesApi";
import { SourceTreeView } from "../components/sources/SourceTreeView";
import type { SourceSelection } from "../types/selection";
import type { PstFolderNode, PstTreeResponse } from "../types/tree";

type Props = {
  selectedSourceId: string | null;
  onOpenImportPreview: () => void;
};

type LoadState = "idle" | "loading" | "ready" | "error";
type SaveState = "idle" | "saving" | "saved" | "error";

function collectDescendantIds(node: PstFolderNode): string[] {
  const ids = [node.id];
  for (const child of node.children) {
    ids.push(...collectDescendantIds(child));
  }
  return ids;
}

function collectExpandableNodeIds(node: PstFolderNode): string[] {
  const ids = [node.id];
  for (const child of node.children) {
    if (child.has_children && child.children.length > 0) {
      ids.push(...collectExpandableNodeIds(child));
    }
  }
  return ids;
}

function getFriendlyErrorMessage(error: unknown, fallback: string): string {
  if (!(error instanceof Error)) {
    return fallback;
  }
  if (error.message.includes("Failed to fetch")) {
    return "API nicht erreichbar. Prüfen Sie, ob das Backend läuft.";
  }
  return error.message;
}

export function PstTreePage({ selectedSourceId, onOpenImportPreview }: Props) {
  const [tree, setTree] = useState<PstTreeResponse | null>(null);
  const [selection, setSelection] = useState<SourceSelection | null>(null);
  const [selectedNodeIds, setSelectedNodeIds] = useState<string[]>([]);
  const [expandedNodeIds, setExpandedNodeIds] = useState<string[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [saveError, setSaveError] = useState<string | null>(null);

  const selectedCount = selection?.selected_count ?? selectedNodeIds.length;
  const selectedPaths = selection?.selected_folder_paths ?? [];

  useEffect(() => {
    if (selectedSourceId === null) {
      setTree(null);
      setSelection(null);
      setSelectedNodeIds([]);
      setExpandedNodeIds([]);
      setLoadState("idle");
      setLoadError(null);
      setSaveState("idle");
      setSaveError(null);
      return;
    }

    setTree(null);
    setSelection(null);
    setSelectedNodeIds([]);
    setExpandedNodeIds([]);
    setLoadState("loading");
    setLoadError(null);
    setSaveState("idle");
    setSaveError(null);

    Promise.all([fetchSourceTree(selectedSourceId), fetchSelection(selectedSourceId)])
      .then(([treeResponse, selectionResponse]) => {
        setTree(treeResponse);
        setSelection(selectionResponse);
        setSelectedNodeIds(selectionResponse.selected_node_ids);
        setExpandedNodeIds(collectExpandableNodeIds(treeResponse.root).slice(0, 8));
        setLoadState("ready");
      })
      .catch((error: unknown) => {
        setLoadState("error");
        setLoadError(getFriendlyErrorMessage(error, "PST-Struktur konnte nicht geladen werden."));
      });
  }, [selectedSourceId]);

  const selectedNodeIdSet = useMemo(() => new Set(selectedNodeIds), [selectedNodeIds]);

  function handleToggleExpand(nodeId: string): void {
    setExpandedNodeIds((current) =>
      current.includes(nodeId) ? current.filter((entry) => entry !== nodeId) : [...current, nodeId]
    );
  }

  function handleToggleSelection(node: PstFolderNode): void {
    const descendantIds = collectDescendantIds(node);

    setSelectedNodeIds((current) => {
      const currentSet = new Set(current);
      const allSelected = descendantIds.every((nodeId) => currentSet.has(nodeId));

      if (allSelected) {
        descendantIds.forEach((nodeId) => currentSet.delete(nodeId));
      } else {
        descendantIds.forEach((nodeId) => currentSet.add(nodeId));
      }

      return Array.from(currentSet);
    });

    setSaveState("idle");
    setSaveError(null);
  }

  async function handleReload(): Promise<void> {
    if (selectedSourceId === null) {
      return;
    }

    setLoadState("loading");
    setLoadError(null);

    try {
      const [treeResponse, selectionResponse] = await Promise.all([
        fetchSourceTree(selectedSourceId),
        fetchSelection(selectedSourceId),
      ]);
      setTree(treeResponse);
      setSelection(selectionResponse);
      setSelectedNodeIds(selectionResponse.selected_node_ids);
      setExpandedNodeIds(collectExpandableNodeIds(treeResponse.root).slice(0, 8));
      setLoadState("ready");
    } catch (error) {
      setLoadState("error");
      setLoadError(getFriendlyErrorMessage(error, "PST-Struktur konnte nicht geladen werden."));
    }
  }

  async function handleSaveSelection(): Promise<void> {
    if (selectedSourceId === null || tree === null) {
      return;
    }

    setSaveState("saving");
    setSaveError(null);

    try {
      const response = await saveSelection(selectedSourceId, selectedNodeIds);
      setSelection(response);
      setSelectedNodeIds(response.selected_node_ids);
      setSaveState("saved");
    } catch (error) {
      setSaveState("error");
      setSaveError(getFriendlyErrorMessage(error, "Auswahl konnte nicht gespeichert werden."));
    }
  }

  return (
    <div className="page">
      <h1>PST-Struktur</h1>

      {selectedSourceId === null && (
        <div className="panel">
          <p className="status-message error">
            Keine PST-Quelle aktiv. Wählen Sie zuerst eine PST-Datei aus.
          </p>
        </div>
      )}

      {selectedSourceId !== null && (
        <div className="panel">
          <div className="panel-actions">
            <div>
              <h2>Ordnerstruktur</h2>
              <p className="hint">Quelle: {selectedSourceId}</p>
              {tree !== null && <p className="hint">Pfad: {tree.source_path}</p>}
            </div>
            <div className="action-bar">
              <button
                type="button"
                className="action-button action-button--secondary"
                onClick={() => void handleReload()}
                disabled={loadState === "loading"}
              >
                {loadState === "loading" ? "Lade ..." : "Neu laden"}
              </button>
              <button
                type="button"
                className="action-button action-button--secondary"
                onClick={() => void handleSaveSelection()}
                disabled={loadState !== "ready" || tree === null || saveState === "saving"}
              >
                {saveState === "saving" ? "Speichere ..." : "Auswahl speichern"}
              </button>
              <button
                type="button"
                className="action-button"
                onClick={onOpenImportPreview}
                disabled={loadState !== "ready" || tree === null}
              >
                Weiter zur Import-Vorschau
              </button>
            </div>
          </div>

          {loadState === "loading" && (
            <p className="status-message pending">PST-Ordnerstruktur wird geladen ...</p>
          )}

          {loadState === "error" && loadError && (
            <div className="status-stack">
              <p className="status-message error">{loadError}</p>
              <p className="hint">
                Prüfen Sie Dateipfad, Netzlaufwerk und Backend-Erreichbarkeit.
              </p>
            </div>
          )}

          {loadState === "ready" && tree !== null && (
            <>
              <div className="pst-tree-summary">
                <span className="pst-tree-summary__label">Root</span>
                <span className="pst-tree-summary__value">{tree.root.name}</span>
                <span className="pst-tree-summary__label">Ausgewählt</span>
                <span className="pst-tree-summary__value">{selectedCount}</span>
              </div>

              {saveState === "saved" && (
                <p className="status-message success">Auswahl wurde im Backend gespeichert.</p>
              )}
              {saveState === "error" && saveError && (
                <p className="status-message error">{saveError}</p>
              )}

              {selectedPaths.length > 0 && (
                <div className="pst-selection-summary">
                  <h3>Vorgemerkte Ordner</h3>
                  <ul className="pst-selection-summary__list">
                    {selectedPaths.map((path) => (
                      <li key={path}>{path}</li>
                    ))}
                  </ul>
                </div>
              )}

              <SourceTreeView
                root={tree.root}
                selectedNodeIds={Array.from(selectedNodeIdSet)}
                expandedNodeIds={expandedNodeIds}
                onToggleExpand={handleToggleExpand}
                onToggleSelection={handleToggleSelection}
              />
            </>
          )}
        </div>
      )}
    </div>
  );
}
