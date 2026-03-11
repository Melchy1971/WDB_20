import { useEffect, useState } from "react";

type Props = {
  selectedFolderPath: string;
  onSelectFolderPath: (path: string) => void;
  onContinueToScan: () => void;
};

export function SourcesPage({ selectedFolderPath, onSelectFolderPath, onContinueToScan }: Props) {
  const [inputValue, setInputValue] = useState(selectedFolderPath);

  // Synchronisiert den lokalen Eingabewert, wenn der zentrale Pfad extern geändert wird
  // (z. B. wenn FolderScanPage den Pfad direkt aktualisiert).
  useEffect(() => {
    setInputValue(selectedFolderPath);
  }, [selectedFolderPath]);

  const isValid = inputValue.trim().length > 0;

  function handleAccept() {
    onSelectFolderPath(inputValue.trim());
  }

  function handleAcceptAndContinue() {
    onSelectFolderPath(inputValue.trim());
    onContinueToScan();
  }

  return (
    <div className="page">
      <h1>Quellenverwaltung</h1>

      <form
        className="panel"
        onSubmit={(e) => {
          e.preventDefault();
          handleAccept();
        }}
      >
        <h2>Ordnerquelle festlegen</h2>
        <label className="label" htmlFor="source-folder-path">
          Ordnerpfad
        </label>
        <input
          id="source-folder-path"
          className="text-input"
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="z. B. /workspace/data/sample_docs"
        />

        {selectedFolderPath && inputValue.trim() !== selectedFolderPath && (
          <p className="hint">
            Aktive Quelle: <strong>{selectedFolderPath}</strong>
          </p>
        )}

        <div className="action-bar">
          <button
            type="button"
            className="action-button action-button--secondary"
            disabled={!isValid}
            onClick={handleAccept}
          >
            Quelle übernehmen
          </button>
          <button
            type="button"
            className="action-button"
            disabled={!isValid}
            onClick={handleAcceptAndContinue}
          >
            Übernehmen und zu Dokumentscan
          </button>
        </div>
      </form>
    </div>
  );
}
