import type { ReactNode } from "react";
import { SidebarNav } from "./SidebarNav";
import type { Page } from "../types/navigation";

type Props = {
  currentPage: Page;
  onNavigate: (page: Page) => void;
  children: ReactNode;
};

export function AppLayout({ currentPage, onNavigate, children }: Props) {
  return (
    <div className="app-layout">
      <SidebarNav currentPage={currentPage} onNavigate={onNavigate} />
      <main className="app-main">{children}</main>
    </div>
  );
}
