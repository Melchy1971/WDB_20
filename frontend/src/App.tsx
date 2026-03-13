import { useEffect, useState } from "react";
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
import { getSelectedSource, selectSource } from "./api/sourcesApi";
import type { AppPage } from "./types/navigation";
import "./index.css";

function App() {
  const [activePage, setActivePage] = useState<AppPage>("system-status");
  const [selectedSourceId, setSelectedSourceId] = useState<string | null>(null);
  const [selectedSourceType, setSelectedSourceType] = useState<string | null>(null);
  const [selectedImportRunId, setSelectedImportRunId] = useState<string | null>(null);

  useEffect(() => {
    getSelectedSource()
      .then((res) => {
        if (res) {
          setSelectedSourceId(res.selected_source_id);
          setSelectedSourceType(res.source_type);
        }
      })
      .catch(() => {});
  }, []);

  async function handleSelectSource(sourceId: string, sourceType: string) {
    await selectSource(sourceId);
    setSelectedSourceId(sourceId);
    setSelectedSourceType(sourceType);
  }

  function renderPage(page: AppPage) {
    switch (page) {
      case "system-status":
        return <SystemStatusPage />;
      case "folder-scan":
        return <FolderScanPage selectedSourceId={selectedSourceId} selectedSourceType={selectedSourceType} onNavigateToPstImport={() => setActivePage("pst-import")} />;
      case "sources":
        return (
          <SourcesPage
            selectedSourceId={selectedSourceId}
            onSelectSource={handleSelectSource}
            onContinueToScan={() => setActivePage("folder-scan")}
          />
        );
      case "topics-review":
        return <TopicsReviewPage />;
      case "pst-import":
        return (
          <PstImportPage
            selectedSourceId={selectedSourceId}
            selectedSourceType={selectedSourceType}
            onOpenPstTree={() => setActivePage("pst-tree")}
            onImported={async (sourceId) => {
              await handleSelectSource(sourceId, "PST");
              setActivePage("pst-import");
            }}
          />
        );
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
