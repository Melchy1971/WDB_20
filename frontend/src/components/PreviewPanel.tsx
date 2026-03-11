type Props = {
  title: string;
  content: string | null;
};

export function PreviewPanel({ title, content }: Props) {
  return (
    <section className="preview-panel">
      <h4 className="preview-panel__title">{title}</h4>
      <div className="preview-box">
        {content ?? <span className="hint">Kein Inhalt verfügbar.</span>}
      </div>
    </section>
  );
}
