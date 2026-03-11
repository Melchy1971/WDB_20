import { useState } from "react";
import { AppLayout } from "./components/layout/AppLayout";
import { SystemStatusPage } from "./pages/SystemStatusPage";
import { FolderScanPage } from "./pages/FolderScanPage";
import { SourcesPage } from "./pages/SourcesPage";
import { TopicsReviewPage } from "./pages/TopicsReviewPage";
import { PstImportPage } from "./pages/PstImportPage";
import { AnalysisPage } from "./pages/AnalysisPage";
import { KiSettingsPage } from "./pages/KiSettingsPage";
import type { ActiveAiProvider } from "./types/ai";
import type { AppPage } from "./types/navigation";
import "./index.css";

function App() {
  const [activePage, setActivePage] = useState<AppPage>("system-status");
  const [selectedFolderPath, setSelectedFolderPath] = useState<string>("");
  const [activeProvider, setActiveProvider] = useState<ActiveAiProvider>("ollama");

  function handleContinueToScan() {
    setActivePage("folder-scan");
  }

  function renderPage(page: AppPage) {
    switch (page) {
      case "system-status":
        return <SystemStatusPage />;
      case "folder-scan":
        return (
          <FolderScanPage
            selectedFolderPath={selectedFolderPath}
            onFolderPathChange={setSelectedFolderPath}
          />
        );
      case "sources":
        return (
          <SourcesPage
            selectedFolderPath={selectedFolderPath}
            onSelectFolderPath={setSelectedFolderPath}
            onContinueToScan={handleContinueToScan}
          />
        );
      case "topics-review":
        return <TopicsReviewPage />;
      case "pst-import":
        return <PstImportPage />;
      case "analysis":
        return <AnalysisPage />;
      case "ki-settings":
        return (
          <KiSettingsPage
            activeProvider={activeProvider}
            onProviderChange={setActiveProvider}
          />
        );
    }
  }

  return (
    <AppLayout activePage={activePage} onNavigate={setActivePage}>
      {renderPage(activePage)}
    </AppLayout>
  );
}

export default App;
