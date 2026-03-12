import { useState } from "react";
import { AppLayout } from "./components/layout/AppLayout";
import { SystemStatusPage } from "./pages/SystemStatusPage";
import { FolderScanPage } from "./pages/FolderScanPage";
import { SourcesPage } from "./pages/SourcesPage";
import { TopicsReviewPage } from "./pages/TopicsReviewPage";
import { PstImportPage } from "./pages/PstImportPage";
import { PstTreePage } from "./pages/PstTreePage";
import { PstImportPreviewPage } from "./pages/PstImportPreviewPage";
import { PstImportRunPage } from "./pages/PstImportRunPage";
import { AnalysisPage } from "./pages/AnalysisPage";
import { KiSettingsPage } from "./pages/KiSettingsPage";
import type { AppPage } from "./types/navigation";
import "./index.css";

function App() {
  const [activePage, setActivePage] = useState<AppPage>("system-status");
  const [selectedSourceId, setSelectedSourceId] = useState<string | null>(null);
  const [selectedImportRunId, setSelectedImportRunId] = useState<string | null>(null);

  function renderPage(page: AppPage) {
    switch (page) {
      case "system-status":
        return <SystemStatusPage />;
      case "folder-scan":
        return <FolderScanPage selectedSourceId={selectedSourceId} />;
      case "sources":
        return (
          <SourcesPage
            selectedSourceId={selectedSourceId}
            onSelectSource={setSelectedSourceId}
            onContinueToScan={() => setActivePage("folder-scan")}
          />
        );
      case "topics-review":
        return <TopicsReviewPage />;
      case "pst-import":
        return <PstImportPage />;
      case "pst-tree":
        return <PstTreePage selectedSourceId={selectedSourceId} />;
      case "pst-import-preview":
        return (
          <PstImportPreviewPage
            selectedSourceId={selectedSourceId}
            onOpenImportRun={(importRunId) => {
              setSelectedImportRunId(importRunId);
              setActivePage("pst-import-run");
            }}
          />
        );
      case "pst-import-run":
        return <PstImportRunPage selectedImportRunId={selectedImportRunId} />;
      case "analysis":
        return <AnalysisPage importRunId={selectedImportRunId} />;
      case "ki-settings":
        return <KiSettingsPage />;
    }
  }

  return (
    <AppLayout activePage={activePage} onNavigate={setActivePage}>
      {renderPage(activePage)}
    </AppLayout>
  );
}

export default App;
