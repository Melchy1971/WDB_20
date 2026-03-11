export type Page = "status" | "sources" | "scan" | "topics";

export type NavItem = {
  page: Page;
  label: string;
};

export const NAV_ITEMS: NavItem[] = [
  { page: "status", label: "System Status" },
  { page: "sources", label: "Quellen" },
  { page: "scan", label: "Ordnerscan" },
  { page: "topics", label: "Themen prüfen" },
];
