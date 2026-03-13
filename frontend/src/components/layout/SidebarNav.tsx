import type { AppPage } from "../../types/navigation";

type Props = {
  activePage: AppPage;
  onNavigate: (page: AppPage) => void;
};

type NavItem = {
  page: AppPage;
  label: string;
};

const ACTIVE_ITEMS: NavItem[] = [
  { page: "system-status", label: "System Status" },
  { page: "folder-scan",   label: "Dokumentscan" },
  { page: "ki-settings",   label: "KI-Einstellungen" },
  { page: "sources",       label: "Quellenverwaltung" },
];

const PST_ITEMS: NavItem[] = [
  { page: "pst-tree",            label: "PST-Struktur" },
  { page: "pst-import-preview",  label: "PST-Import-Vorschau" },
  { page: "pst-import-run",      label: "PST-Import Ergebnis" },
  { page: "pst-import",          label: "PST-Import" },
];

const FUTURE_ITEMS: NavItem[] = [
  { page: "topics-review",  label: "Themenreview" },
  { page: "analysis",       label: "KI-Analyse" },
];

export function SidebarNav({ activePage, onNavigate }: Props) {
  function navButton(item: NavItem, muted = false) {
    const isActive = activePage === item.page;
    return (
      <li key={item.page}>
        <button
          type="button"
          className={`nav-btn${isActive ? " nav-btn--active" : ""}${muted ? " nav-btn--muted" : ""}`}
          onClick={() => onNavigate(item.page)}
          aria-current={isActive ? "page" : undefined}
        >
          {item.label}
        </button>
      </li>
    );
  }

  return (
    <nav className="app-sidebar">
      <div className="brand-header">
        <div className="brand-mark" aria-hidden="true">T</div>
        <div className="brand-text">
          <span className="brand-title">TeleMail KP</span>
          <span className="brand-subtitle">Knowledge Platform</span>
        </div>
      </div>

      <div className="nav-section">
        <div className="nav-section-title">Aktiv</div>
        <ul className="nav-list">
          {ACTIVE_ITEMS.map((item) => navButton(item))}
        </ul>
      </div>

      <div className="nav-section">
        <div className="nav-section-title">PST-Datei</div>
        <ul className="nav-list">
          {PST_ITEMS.map((item) => navButton(item, true))}
        </ul>
      </div>

      <div className="nav-section">
        <div className="nav-section-title">Nächste Ausbaustufen</div>
        <ul className="nav-list">
          {FUTURE_ITEMS.map((item) => navButton(item, true))}
        </ul>
      </div>
    </nav>
  );
}
