import { useState } from "react";

type Props = {
  onScan: (folderPath: string) => Promise<void>;
  isLoading: boolean;
};

export function FolderScanForm({ onScan, isLoading }: Props) {
  const [folderPath, setFolderPath] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await onScan(folderPath.trim());
  }

  return (
    <form className="panel" onSubmit={handleSubmit}>
      <h2>Lokalen Ordner scannen</h2>
      <label className="label" htmlFor="folder-path">
        Ordnerpfad
      </label>
      <input
        id="folder-path"
        className="text-input"
        type="text"
        value={folderPath}
        onChange={(e) => setFolderPath(e.target.value)}
        placeholder="z. B. /workspace/data/sample_docs"
        required
      />
      <button
        className="action-button"
        type="submit"
        disabled={isLoading || folderPath.trim().length === 0}
      >
        {isLoading ? "Scanne ..." : "Ordner scannen"}
      </button>
    </form>
  );
}
