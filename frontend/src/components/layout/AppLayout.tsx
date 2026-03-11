import type { ReactNode } from "react";
import { SidebarNav } from "./SidebarNav";
import type { AppPage } from "../../types/navigation";

type Props = {
  children: ReactNode;
  activePage: AppPage;
  onNavigate: (page: AppPage) => void;
};

export function AppLayout({ children, activePage, onNavigate }: Props) {
  return (
    <div className="app-layout">
      <SidebarNav activePage={activePage} onNavigate={onNavigate} />
      <main className="app-main">{children}</main>
    </div>
  );
}
