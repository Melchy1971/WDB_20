import { NAV_ITEMS } from "../types/navigation";
import type { Page } from "../types/navigation";

type Props = {
  currentPage: Page;
  onNavigate: (page: Page) => void;
};

export function SidebarNav({ currentPage, onNavigate }: Props) {
  return (
    <nav className="sidebar-nav">
      <div className="sidebar-logo">
        <span className="sidebar-logo__icon">✉</span>
        <span className="sidebar-logo__text">Mail Knowledge</span>
      </div>
      <ul className="nav-list" role="list">
        {NAV_ITEMS.map(({ page, label }) => (
          <li key={page}>
            <button
              className={`nav-item${currentPage === page ? " nav-item--active" : ""}`}
              onClick={() => onNavigate(page)}
              type="button"
              aria-current={currentPage === page ? "page" : undefined}
            >
              {label}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}
