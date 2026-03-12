export type AnalysisPriority = "low" | "medium" | "high";

export type AnalysisResult = {
  topic_label: string;
  summary: string;
  keywords: string[];
  entities: string[];
  priority: AnalysisPriority;
  confidence: number;
};

export type StartImportRunAnalysisRequest = Record<string, never>;

export type StartImportRunAnalysisResponse = {
  import_run_id: string;
  status: "queued" | "running" | "finished" | "failed";
  message: string;
};

export type ImportRunAnalysisResponse = {
  import_run_id: string;
  status: "queued" | "running" | "finished" | "failed";
  results: AnalysisResult[];
};
