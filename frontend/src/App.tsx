import { useState } from "react";
import { AppLayout } from "./components/layout/AppLayout";
import { SystemStatusPage } from "./pages/SystemStatusPage";
import { FolderScanPage } from "./pages/FolderScanPage";
import { SourcesPage } from "./pages/SourcesPage";
import { TopicsReviewPage } from "./pages/TopicsReviewPage";
import { PstImportPage } from "./pages/PstImportPage";
import { AnalysisPage } from "./pages/AnalysisPage";
import type { AppPage } from "./types/navigation";
import "./index.css";

function renderPage(page: AppPage) {
  switch (page) {
    case "system-status":   return <SystemStatusPage />;
    case "folder-scan":     return <FolderScanPage />;
    case "sources":         return <SourcesPage />;
    case "topics-review":   return <TopicsReviewPage />;
    case "pst-import":      return <PstImportPage />;
    case "analysis":        return <AnalysisPage />;
  }
}

function App() {
  const [activePage, setActivePage] = useState<AppPage>("system-status");

  return (
    <AppLayout activePage={activePage} onNavigate={setActivePage}>
      {renderPage(activePage)}
    </AppLayout>
  );
}

export default App;
