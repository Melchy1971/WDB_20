import type { TreeNode, TreeNodeType } from "../../types/tree";

const NODE_ICONS: Record<TreeNodeType, string> = {
  folder: "▶",
  message: "✉",
  attachment: "⊘",
};

type NodeProps = {
  node: TreeNode;
  selectedNodeIds: string[];
  onToggleNode: (nodeId: string) => void;
};

function TreeNodeRow({ node, selectedNodeIds, onToggleNode }: NodeProps) {
  const icon = NODE_ICONS[node.node_type];
  const isSelected = selectedNodeIds.includes(node.id);

  return (
    <div className="tree-node">
      <div className={`tree-node__row${isSelected ? " tree-node__row--selected" : ""}`}>
        <input
          type="checkbox"
          className="tree-node__checkbox"
          checked={isSelected}
          onChange={() => onToggleNode(node.id)}
          aria-label={node.name}
        />
        <span className="tree-node__icon" aria-hidden="true">{icon}</span>
        <span className="tree-node__name">{node.name}</span>
        {node.item_count !== undefined && (
          <span className="tree-node__count">{node.item_count}</span>
        )}
      </div>
      {node.children.map((child) => (
        <TreeNodeRow
          key={child.id}
          node={child}
          selectedNodeIds={selectedNodeIds}
          onToggleNode={onToggleNode}
        />
      ))}
    </div>
  );
}

type Props = {
  root: TreeNode;
  selectedNodeIds: string[];
  onToggleNode: (nodeId: string) => void;
};

export function SourceTreeView({ root, selectedNodeIds, onToggleNode }: Props) {
  return (
    <div className="tree-root">
      <TreeNodeRow
        node={root}
        selectedNodeIds={selectedNodeIds}
        onToggleNode={onToggleNode}
      />
    </div>
  );
}
