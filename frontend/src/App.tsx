import { useState } from "react";
import "./index.css";
import { AppLayout } from "./components/AppLayout";
import { SystemStatusPage } from "./pages/SystemStatusPage";
import { SourcesPage } from "./pages/SourcesPage";
import { FolderScanPage } from "./pages/FolderScanPage";
import { TopicsReviewPage } from "./pages/TopicsReviewPage";
import type { Page } from "./types/navigation";

function App() {
  const [currentPage, setCurrentPage] = useState<Page>("status");

  const pages: Record<Page, JSX.Element> = {
    status: <SystemStatusPage />,
    sources: <SourcesPage />,
    scan: <FolderScanPage />,
    topics: <TopicsReviewPage />,
  };

  return (
    <AppLayout currentPage={currentPage} onNavigate={setCurrentPage}>
      {pages[currentPage]}
    </AppLayout>
  );
}

export default App;
