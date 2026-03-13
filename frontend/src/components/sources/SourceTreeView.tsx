import { useEffect, useMemo, useRef } from "react";

import type { PstFolderNode } from "../../types/tree";

type TreeNodeSelectionState = "checked" | "partial" | "unchecked";

function collectDescendantIds(node: PstFolderNode): string[] {
  const ids = [node.id];
  for (const child of node.children) {
    ids.push(...collectDescendantIds(child));
  }
  return ids;
}

function getSelectionState(node: PstFolderNode, selectedNodeIds: Set<string>): TreeNodeSelectionState {
  const descendantIds = collectDescendantIds(node);
  const selectedCount = descendantIds.filter((nodeId) => selectedNodeIds.has(nodeId)).length;

  if (selectedCount === 0) {
    return "unchecked";
  }
  if (selectedCount === descendantIds.length) {
    return "checked";
  }
  return "partial";
}

type PstTreeNodeProps = {
  node: PstFolderNode;
  selectedNodeIds: Set<string>;
  expandedNodeIds: Set<string>;
  onToggleExpand: (nodeId: string) => void;
  onToggleSelection: (node: PstFolderNode) => void;
  level?: number;
};

function PstTreeNode({
  node,
  selectedNodeIds,
  expandedNodeIds,
  onToggleExpand,
  onToggleSelection,
  level = 0,
}: PstTreeNodeProps) {
  const checkboxRef = useRef<HTMLInputElement | null>(null);
  const canExpand = node.has_children && node.children.length > 0;
  const isExpanded = expandedNodeIds.has(node.id);
  const selectionState = getSelectionState(node, selectedNodeIds);

  useEffect(() => {
    if (checkboxRef.current !== null) {
      checkboxRef.current.indeterminate = selectionState === "partial";
    }
  }, [selectionState]);

  return (
    <div className="tree-node" role="treeitem" aria-expanded={canExpand ? isExpanded : undefined}>
      <div className="tree-node__row">
        <button
          type="button"
          className="tree-node__toggle"
          onClick={() => onToggleExpand(node.id)}
          disabled={!canExpand}
          aria-label={canExpand ? `${isExpanded ? "Zuklappen" : "Aufklappen"} ${node.name}` : `${node.name} hat keine Unterordner`}
        >
          {canExpand ? (isExpanded ? "v" : ">") : "•"}
        </button>
        <input
          ref={checkboxRef}
          type="checkbox"
          className="tree-node__checkbox"
          checked={selectionState === "checked"}
          onChange={() => onToggleSelection(node)}
          aria-label={`Ordner ${node.name} auswählen`}
        />
        <span className="tree-node__name" title={node.path}>
          {node.name}
        </span>
        <span className="tree-node__count">{node.message_count}</span>
      </div>

      {canExpand && isExpanded && (
        <div className="tree-node__children" role="group">
          {node.children.map((child) => (
            <PstTreeNode
              key={child.id}
              node={child}
              selectedNodeIds={selectedNodeIds}
              expandedNodeIds={expandedNodeIds}
              onToggleExpand={onToggleExpand}
              onToggleSelection={onToggleSelection}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

type Props = {
  root: PstFolderNode;
  selectedNodeIds: string[];
  expandedNodeIds: string[];
  onToggleExpand: (nodeId: string) => void;
  onToggleSelection: (node: PstFolderNode) => void;
};

export function SourceTreeView({
  root,
  selectedNodeIds,
  expandedNodeIds,
  onToggleExpand,
  onToggleSelection,
}: Props) {
  const selectedNodeIdSet = useMemo(() => new Set(selectedNodeIds), [selectedNodeIds]);
  const expandedNodeIdSet = useMemo(() => new Set(expandedNodeIds), [expandedNodeIds]);

  return (
    <div className="tree-root" role="tree" aria-label="PST-Ordnerstruktur">
      <PstTreeNode
        node={root}
        selectedNodeIds={selectedNodeIdSet}
        expandedNodeIds={expandedNodeIdSet}
        onToggleExpand={onToggleExpand}
        onToggleSelection={onToggleSelection}
      />
    </div>
  );
}
