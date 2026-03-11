import { useState } from "react";
import type { CreateSourceRequest, SourceType } from "../../types/document";

type Props = {
  onSubmit: (data: CreateSourceRequest) => Promise<void>;
  isLoading: boolean;
};

export function SourceForm({ onSubmit, isLoading }: Props) {
  const [name, setName] = useState("");
  const [type, setType] = useState<SourceType>("folder");
  const [path, setPath] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await onSubmit({ name, type, path });
    setName("");
    setPath("");
  }

  return (
    <form className="source-form" onSubmit={handleSubmit}>
      <label className="label" htmlFor="source-name">
        Name
      </label>
      <input
        id="source-name"
        className="text-input"
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="z. B. Posteingang 2024"
        required
      />

      <label className="label" htmlFor="source-type">
        Typ
      </label>
      <select
        id="source-type"
        className="text-input"
        value={type}
        onChange={(e) => setType(e.target.value as SourceType)}
      >
        <option value="folder">Ordner</option>
        <option value="pst">PST-Datei</option>
        <option value="imap">IMAP</option>
      </select>

      <label className="label" htmlFor="source-path">
        Pfad / Adresse
      </label>
      <input
        id="source-path"
        className="text-input"
        type="text"
        value={path}
        onChange={(e) => setPath(e.target.value)}
        placeholder="z. B. /data/mails oder imap.example.com"
        required
      />

      <button className="action-button" type="submit" disabled={isLoading}>
        {isLoading ? "Speichere ..." : "Quelle anlegen"}
      </button>
    </form>
  );
}
