import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ApiError, getStatsSummary, getStatsTimeseries } from "../api/client";
import type { StatsSummaryResponse, StatsTimeseriesResponse } from "../types/detection";

interface StatsChartsProps {
  refreshToken: number;
}

const COLOR_TOTAL = "#3b82f6";
const COLOR_VIOLATION = "#ef4444";

export function StatsCharts({ refreshToken }: StatsChartsProps) {
  const [summary, setSummary] = useState<StatsSummaryResponse | null>(null);
  const [timeseries, setTimeseries] = useState<StatsTimeseriesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    Promise.all([getStatsSummary(), getStatsTimeseries()])
      .then(([summaryResponse, timeseriesResponse]) => {
        if (!isActive) return;
        setSummary(summaryResponse);
        setTimeseries(timeseriesResponse);
      })
      .catch((err) => {
        if (!isActive) return;
        setError(err instanceof ApiError ? err.message : "Failed to load statistics.");
      });

    return () => {
      isActive = false;
    };
  }, [refreshToken]);

  if (error) {
    return (
      <section className="card">
        <h2>Statistics</h2>
        <p className="error-text">{error}</p>
      </section>
    );
  }

  return (
    <section className="card">
      <h2>Statistics</h2>

      {summary && (
        <div className="kpi-row">
          <KpiCard label="Media assets" value={summary.total_media_assets} />
          <KpiCard label="Total detections" value={summary.total_detections} />
          <KpiCard label="Total violations" value={summary.total_violations} />
          <KpiCard label="Compliance rate" value={`${(summary.compliance_rate * 100).toFixed(1)}%`} />
        </div>
      )}

      <div className="chart-grid">
        <div className="chart-box">
          <h3>Detections by class</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={summary?.by_class ?? []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="class_name" tick={{ fontSize: 11 }} interval={0} angle={-30} textAnchor="end" height={70} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="total_detections" name="Total" fill={COLOR_TOTAL} />
              <Bar dataKey="total_violations" name="Violations" fill={COLOR_VIOLATION} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-box">
          <h3>Detections over time</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={timeseries?.points ?? []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="bucket_start"
                tick={{ fontSize: 11 }}
                tickFormatter={(value: string) => new Date(value).toLocaleDateString()}
              />
              <YAxis allowDecimals={false} />
              <Tooltip labelFormatter={(value: string) => new Date(value).toLocaleDateString()} />
              <Line type="monotone" dataKey="total_detections" name="Total" stroke={COLOR_TOTAL} strokeWidth={2} />
              <Line type="monotone" dataKey="total_violations" name="Violations" stroke={COLOR_VIOLATION} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}

function KpiCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="kpi-card">
      <span className="kpi-value">{value}</span>
      <span className="kpi-label">{label}</span>
    </div>
  );
}
