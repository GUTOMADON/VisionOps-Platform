import { useState } from "react";

import { DetectionResults } from "../components/DetectionResults";
import { HistoryTable } from "../components/HistoryTable";
import { StatsCharts } from "../components/StatsCharts";
import { UploadPanel } from "../components/UploadPanel";
import type { InferenceResponse } from "../types/detection";

export function Dashboard() {
  const [latestResult, setLatestResult] = useState<InferenceResponse | null>(null);
  const [refreshToken, setRefreshToken] = useState(0);

  function handleResult(result: InferenceResponse) {
    setLatestResult(result);
    setRefreshToken((current) => current + 1);
  }

  return (
    <div className="dashboard-grid">
      <UploadPanel onResult={handleResult} />
      {latestResult && <DetectionResults result={latestResult} />}
      <StatsCharts refreshToken={refreshToken} />
      <HistoryTable refreshToken={refreshToken} />
    </div>
  );
}
